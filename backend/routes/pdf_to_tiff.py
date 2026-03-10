from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pdf2image import convert_from_path
import os, uuid, zipfile, threading, time, shutil, asyncio, json

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

TTL_SECONDS = 30 * 60  # 30 minutes

# ================= STORES =================
progress_store = {}   # job_id -> progress %
job_status = {}       # processing | zipping | completed
job_created_at = {}   # job_id -> timestamp

# ================= WORKER =================
def run_pdf_to_tiff(job_id: str, pdf_path: str):
    try:
        tiff_dir = os.path.join(OUTPUT_DIR, f"{job_id}_tiff")
        zip_path = os.path.join(OUTPUT_DIR, f"{job_id}_tiff.zip")
        os.makedirs(tiff_dir, exist_ok=True)

        progress_store[job_id] = 5

        images = convert_from_path(pdf_path, dpi=300, fmt="tiff")
        total = len(images)

        for i, img in enumerate(images):
            img.save(
                os.path.join(tiff_dir, f"page_{i+1}.tiff"),
                format="TIFF"
            )
            progress_store[job_id] = int(((i + 1) / total) * 80) + 10

        job_status[job_id] = "zipping"
        progress_store[job_id] = 92

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in sorted(os.listdir(tiff_dir)):
                zipf.write(os.path.join(tiff_dir, f), arcname=f)

        progress_store[job_id] = 100
        job_status[job_id] = "completed"

    except Exception as e:
        print("❌ TIFF failed:", e)
        progress_store[job_id] = 100
        job_status[job_id] = "completed"

# ================= START =================
@router.post("/pdf-to-tiff")
async def pdf_to_tiff(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{job_id}.pdf")

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    progress_store[job_id] = 1
    job_status[job_id] = "processing"
    job_created_at[job_id] = time.time()

    threading.Thread(
        target=run_pdf_to_tiff,
        args=(job_id, pdf_path),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "progress_url": f"/events/pdf-to-tiff-progress/{job_id}",
        "download_url": f"/download-tiff/{job_id}"
    }

# ================= SSE =================
@router.get("/events/pdf-to-tiff-progress/{job_id}")
async def pdf_to_tiff_progress(job_id: str):

    async def event_generator():
        last = -1
        while True:
            progress = progress_store.get(job_id, 0)

            if progress != last:
                yield f"data: {json.dumps({'progress': progress})}\n\n"
                last = progress

            if progress >= 100 and job_status.get(job_id) == "completed":
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ================= CLEANUP =================
def cleanup_job(job_id: str):
    time.sleep(2)

    paths = [
        os.path.join(UPLOAD_DIR, f"{job_id}.pdf"),
        os.path.join(OUTPUT_DIR, f"{job_id}_tiff"),
        os.path.join(OUTPUT_DIR, f"{job_id}_tiff.zip"),
    ]

    for p in paths:
        if os.path.exists(p):
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    progress_store.pop(job_id, None)
    job_status.pop(job_id, None)
    job_created_at.pop(job_id, None)

# ================= TTL AUTO CLEANUP =================
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

# ================= DOWNLOAD =================
@router.get("/download-tiff/{job_id}")
def download_tiff(job_id: str, background_tasks: BackgroundTasks):
    zip_path = os.path.join(OUTPUT_DIR, f"{job_id}_tiff.zip")

    if not os.path.exists(zip_path):
        raise HTTPException(404, "File expired or not ready")

    background_tasks.add_task(cleanup_job, job_id)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="pdf_to_tiff.zip"
    )
