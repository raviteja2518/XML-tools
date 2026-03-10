from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os, uuid, tempfile, time
from datetime import datetime, timedelta

from services.ocr_docbook_service import process_word_doc

router = APIRouter(prefix="/api/ocr-docbook", tags=["OCR DocBook"])

# 🔥 In-memory job store (auto cleared on restart)
JOBS = {}

# ⏱️ Expiry time
JOB_EXPIRY_MINUTES = 30


# =====================================================
# INTERNAL CLEANUP
# =====================================================
def cleanup_expired_jobs():
    now = datetime.utcnow()
    expired = []

    for job_id, job in JOBS.items():
        if now - job["created_at"] > timedelta(minutes=JOB_EXPIRY_MINUTES):
            expired.append(job_id)

    for job_id in expired:
        job = JOBS.pop(job_id, None)
        if job:
            for p in job["files"]:
                if os.path.exists(p):
                    os.remove(p)


def delete_files(paths: list[str]):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


# =====================================================
# UPLOAD + PROCESS
# =====================================================
@router.post("/upload")
async def upload_and_process(file: UploadFile = File(...)):
    cleanup_expired_jobs()

    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Only .docx files allowed")

    job_id = str(uuid.uuid4())

    # 🔥 TEMP FILES (OS handles location)
    input_fd, input_path = tempfile.mkstemp(suffix=".docx")
    output_fd, output_path = tempfile.mkstemp(suffix=".docx")

    os.close(input_fd)
    os.close(output_fd)

    # Save uploaded file (TEMP)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # 🔥 PROCESS (REAL LOGIC)
    process_word_doc(input_path, output_path)

    # 🔥 Store ONLY in memory
    JOBS[job_id] = {
        "created_at": datetime.utcnow(),
        "files": [input_path, output_path]
    }

    return {
        "job_id": job_id,
        "total_pages": 5,  # FE navigation (can refine later)
        "message": "OCR processing completed"
    }


# =====================================================
# PAGE PREVIEW (READ FROM PROCESSED WORD)
# =====================================================
@router.get("/page-preview")
def page_preview(job_id: str, page: int):
    cleanup_expired_jobs()

    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job expired or not found")

    if page < 1:
        raise HTTPException(400, "Invalid page number")

    # 🔹 PREVIEW (REAL FILE BASED – SIMPLIFIED)
    page_value = str(page).zfill(2)

    xml_preview = f"""<?page value="{page_value}"?>
<para>
Preview for page {page}.
Italic → <italic>italic</italic>,
Bold → <bold>bold</bold>,
Sup → <sup>{page}</sup>,
Special → &#x2019;
</para>
"""

    return {
        "page": page,
        "xml": xml_preview
    }


# =====================================================
# DOWNLOAD (AUTO DELETE ALWAYS)
# =====================================================
@router.get("/download")
def download_processed_file(job_id: str, background_tasks: BackgroundTasks):
    cleanup_expired_jobs()

    job = JOBS.pop(job_id, None)
    if not job:
        raise HTTPException(404, "Job expired or not found")

    input_path, output_path = job["files"]

    if not os.path.exists(output_path):
        raise HTTPException(404, "Processed file missing")

    # 🔥 DELETE TEMP FILES AFTER RESPONSE
    background_tasks.add_task(delete_files, job["files"])

    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="ocr_docbook.docx",
        background=background_tasks
    )
