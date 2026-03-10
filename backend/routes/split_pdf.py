from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pypdf import PdfReader, PdfWriter
import uuid, os, time, threading, shutil, zipfile

router = APIRouter()

# ================= CONFIG =================
BASE_TMP = "tmp/jobs"
TTL_SECONDS = 30 * 60  # 30 minutes

os.makedirs(BASE_TMP, exist_ok=True)

progress_map = {}
job_created_at = {}

# ================= CLEANUP THREAD =================
def cleanup_worker():
    while True:
        now = time.time()
        for job_id in list(job_created_at.keys()):
            if now - job_created_at[job_id] > TTL_SECONDS:
                job_dir = os.path.join(BASE_TMP, job_id)
                if os.path.exists(job_dir):
                    shutil.rmtree(job_dir, ignore_errors=True)
                    print(f"🧹 TTL cleanup: {job_id}")
                progress_map.pop(job_id, None)
                job_created_at.pop(job_id, None)
        time.sleep(60)

threading.Thread(target=cleanup_worker, daemon=True).start()

# ================= HELPERS =================
def parse_ranges(ranges_str: str, total_pages: int):
    ranges = []
    for part in ranges_str.split(","):
        part = part.strip()
        if "-" in part:
            s, e = map(int, part.split("-"))
        else:
            s = e = int(part)

        # ❌ strict validation
        if s < 1 or e < 1 or s > e or e > total_pages:
            raise ValueError(f"Invalid range: {s}-{e} (PDF has {total_pages} pages)")

        ranges.append((s, e))
    return ranges

# ================= SPLIT JOB =================
def split_pdf_job(job_id, pdf_path, ranges):
    try:
        progress_map[job_id] = 5

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        job_dir = os.path.join(BASE_TMP, job_id)
        parts_dir = os.path.join(job_dir, "parts")
        os.makedirs(parts_dir, exist_ok=True)

        total_parts = len(ranges)

        # ---- SPLIT ----
        for idx, (start, end) in enumerate(ranges):
            writer = PdfWriter()
            for p in range(start - 1, end):
                writer.add_page(reader.pages[p])

            tmp_pdf = os.path.join(parts_dir, f"tmp_{idx+1:02d}.pdf")
            with open(tmp_pdf, "wb") as f:
                writer.write(f)

            progress_map[job_id] = int(((idx + 1) / total_parts) * 80)

        # ---- ZIP CREATION ----
        zip_path = os.path.join(job_dir, "output.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in sorted(os.listdir(parts_dir)):
                zipf.write(os.path.join(parts_dir, f), arcname=f)

        progress_map[job_id] = 100

    except Exception as e:
        print("❌ Split error:", e)
        progress_map[job_id] = -1

# ================= API =================
@router.post("/pdf/split-range")
async def split_pdf(
    file: UploadFile = File(...),
    ranges: str = Form(...)
):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_TMP, job_id)
    os.makedirs(job_dir, exist_ok=True)

    pdf_path = os.path.join(job_dir, "input.pdf")
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    try:
        parsed_ranges = parse_ranges(ranges, total_pages)
    except ValueError as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))

    job_created_at[job_id] = time.time()
    progress_map[job_id] = 0

    threading.Thread(
        target=split_pdf_job,
        args=(job_id, pdf_path, parsed_ranges),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "progress_url": f"/pdf/split/progress/{job_id}",
        "download_url": f"/pdf/split/download/{job_id}"
    }

# ================= SSE =================
@router.get("/pdf/split/progress/{job_id}")
def progress_sse(job_id: str):
    def stream():
        last = None
        while True:
            val = progress_map.get(job_id)
            if val is None:
                break
            if val != last:
                yield f"data: {val}\n\n"
                last = val
            if val >= 100 or val < 0:
                break
            time.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")

# ================= DOWNLOAD =================
@router.get("/pdf/split/download/{job_id}")
def download_zip(job_id: str, name: str = "chapter"):
    job_dir = os.path.join(BASE_TMP, job_id)
    parts_dir = os.path.join(job_dir, "parts")
    src_zip = os.path.join(job_dir, "output.zip")

    if not os.path.exists(src_zip):
        raise HTTPException(404, "File expired or not ready")

    final_zip = os.path.join(job_dir, f"{name}.zip")

    # Rename PDFs inside ZIP
    with zipfile.ZipFile(final_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for idx, f in enumerate(sorted(os.listdir(parts_dir))):
            zipf.write(
                os.path.join(parts_dir, f),
                arcname=f"{name}{idx+1:02d}.pdf"
            )

    # ⏳ delayed cleanup (Windows safe)
    def cleanup():
        time.sleep(10)
        shutil.rmtree(job_dir, ignore_errors=True)
        progress_map.pop(job_id, None)
        job_created_at.pop(job_id, None)
        print(f"🧹 Job cleaned: {job_id}")

    threading.Thread(target=cleanup, daemon=True).start()

    return FileResponse(
        final_zip,
        media_type="application/zip",
        filename=f"{name}.zip"
    )
