from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pypdf import PdfReader, PdfWriter
import os, uuid, zipfile, time, shutil, threading, asyncio, json

router = APIRouter()

# ===============================
# PATHS
# ===============================
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

TTL_SECONDS = 30 * 60  # 30 minutes

# ===============================
# IN-MEMORY STORES
# ===============================
progress_store = {}      # job_id -> progress (0–100)
job_created_at = {}      # job_id -> timestamp
job_status = {}          # job_id -> processing | completed


# ===============================
# RANGE PARSER
# ===============================
def parse_ranges(ranges: str):
    result = []
    for part in ranges.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            result.append((int(a), int(b)))
        else:
            p = int(part)
            result.append((p, p))
    return result


# ===============================
# BACKGROUND SPLIT WORKER
# ===============================
def split_worker(job_id: str, pdf_path: str, ranges: str):
    try:
        progress_store[job_id] = 5

        out_dir = os.path.join(OUTPUT_DIR, f"{job_id}_split")
        zip_path = os.path.join(OUTPUT_DIR, f"{job_id}_split.zip")
        os.makedirs(out_dir, exist_ok=True)

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        parsed = parse_ranges(ranges)

        total_steps = sum((min(e, total_pages) - s + 1) for s, e in parsed)
        done = 0

        for start, end in parsed:
            writer = PdfWriter()
            for p in range(start - 1, min(end, total_pages)):
                writer.add_page(reader.pages[p])
                done += 1
                progress_store[job_id] = int((done / total_steps) * 80) + 10

            out_pdf = os.path.join(out_dir, f"range_{start}_{end}.pdf")
            with open(out_pdf, "wb") as f:
                writer.write(f)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in sorted(os.listdir(out_dir)):
                zipf.write(os.path.join(out_dir, f), arcname=f)

        progress_store[job_id] = 100
        job_status[job_id] = "completed"

    except Exception as e:
        print("❌ Split failed:", e)
        progress_store[job_id] = 100
        job_status[job_id] = "completed"


# ===============================
# START SPLIT API
# ===============================
@router.post("/pdf-split")
async def pdf_split(file: UploadFile = File(...), ranges: str = Form(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{job_id}.pdf")

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    progress_store[job_id] = 0
    job_created_at[job_id] = time.time()
    job_status[job_id] = "processing"

    threading.Thread(
        target=split_worker,
        args=(job_id, pdf_path, ranges),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "progress_url": f"/events/pdf-split-progress/{job_id}",
        "download_url": f"/download-split/{job_id}"
    }


# ===============================
# SSE PROGRESS (BEST PRACTICE)
# ===============================
@router.get("/events/pdf-split-progress/{job_id}")
async def split_progress(job_id: str):

    async def event_generator():
        last = -1
        while True:
            p = progress_store.get(job_id, 0)
            if p != last:
                yield f"data: {json.dumps({'progress': p})}\n\n"
                last = p
            if p >= 100:
                break
            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# ===============================
# CLEANUP JOB
# ===============================
def cleanup_job(job_id: str):
    time.sleep(2)  # allow download to finish

    paths = [
        os.path.join(UPLOAD_DIR, f"{job_id}.pdf"),
        os.path.join(OUTPUT_DIR, f"{job_id}_split"),
        os.path.join(OUTPUT_DIR, f"{job_id}_split.zip"),
    ]

    for p in paths:
        if os.path.exists(p):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)

    progress_store.pop(job_id, None)
    job_created_at.pop(job_id, None)
    job_status.pop(job_id, None)


# ===============================
# TTL AUTO CLEANUP (SAFE)
# ===============================
def ttl_cleanup_worker():
    while True:
        now = time.time()
        for job_id in list(job_created_at.keys()):
            if (
                job_status.get(job_id) == "completed"
                and now - job_created_at[job_id] > TTL_SECONDS
            ):
                cleanup_job(job_id)
        time.sleep(300)  # every 5 mins


threading.Thread(target=ttl_cleanup_worker, daemon=True).start()


# ===============================
# DOWNLOAD + AUTO DELETE
# ===============================
@router.get("/download-split/{job_id}")
def download_split(job_id: str, background_tasks: BackgroundTasks):
    zip_path = os.path.join(OUTPUT_DIR, f"{job_id}_split.zip")

    if not os.path.exists(zip_path):
        raise HTTPException(404, "File expired or not ready")

    background_tasks.add_task(cleanup_job, job_id)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="pdf_split.zip",
        headers={
            "X-Job-Completed": "true"  # FE reset signal
        }
    )
