from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pdf2image import convert_from_path, pdfinfo_from_path
from bs4 import BeautifulSoup
from docx import Document
import pytesseract
import uuid, os, threading, time, shutil, asyncio, json

router = APIRouter()

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OCR_DIR = os.path.join(BASE_DIR, "storage", "ocr")

os.makedirs(OCR_DIR, exist_ok=True)

ENTITY_FILE = os.path.join(DATA_DIR, "entities.html")
TTL_SECONDS = 30 * 60  # 30 minutes

# ================= IN-MEMORY STORES =================
progress_store = {}    # job_id -> progress %
job_status = {}        # processing | completed
job_created_at = {}    # job_id -> timestamp

# ================= ENTITY MAP =================
def load_entity_map():
    if not os.path.exists(ENTITY_FILE):
        return {}

    soup = BeautifulSoup(open(ENTITY_FILE, encoding="utf-8"), "html.parser")
    table = soup.find("table")
    mapping = {}

    if table:
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                mapping[cols[-1].text.strip()] = cols[-2].text.strip()

    return mapping

ENTITY_MAP = load_entity_map()

def replace_entities(text: str) -> str:
    return "".join(ENTITY_MAP.get(ch, ch) for ch in text)

# ================= OCR WORKER =================
def ocr_job(job_id: str, pdf_path: str):
    try:
        progress_store[job_id] = 5

        info = pdfinfo_from_path(pdf_path)
        total_pages = info["Pages"]

        doc = Document()

        for page in range(1, total_pages + 1):
            images = convert_from_path(
                pdf_path,
                dpi=300,
                first_page=page,
                last_page=page
            )

            text = pytesseract.image_to_string(images[0])
            text = replace_entities(text)

            doc.add_paragraph(text)

            progress_store[job_id] = int((page / total_pages) * 90) + 5

        out_path = os.path.join(OCR_DIR, f"{job_id}.docx")
        doc.save(out_path)

        progress_store[job_id] = 100
        job_status[job_id] = "completed"

    except Exception as e:
        print("❌ OCR FAILED:", e)
        progress_store[job_id] = 100
        job_status[job_id] = "completed"

# ================= START OCR =================
@router.post("/tools/pdf-to-word-ocr")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())
    pdf_path = os.path.join(OCR_DIR, f"{job_id}.pdf")

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    progress_store[job_id] = 1
    job_status[job_id] = "processing"
    job_created_at[job_id] = time.time()

    threading.Thread(
        target=ocr_job,
        args=(job_id, pdf_path),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "progress_url": f"/events/pdf-to-word-ocr-progress/{job_id}",
        "download_url": f"/tools/download/{job_id}"
    }

# ================= SSE PROGRESS =================
@router.get("/events/pdf-to-word-ocr-progress/{job_id}")
async def ocr_progress(job_id: str):

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

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# ================= CLEANUP =================
def cleanup_job(job_id: str):
    time.sleep(2)

    paths = [
        os.path.join(OCR_DIR, f"{job_id}.pdf"),
        os.path.join(OCR_DIR, f"{job_id}.docx"),
    ]

    for p in paths:
        if os.path.exists(p):
            os.remove(p)

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
        time.sleep(300)

threading.Thread(target=ttl_cleanup_worker, daemon=True).start()

# ================= DOWNLOAD =================
@router.get("/tools/download/{job_id}")
def download(job_id: str, background_tasks: BackgroundTasks):
    path = os.path.join(OCR_DIR, f"{job_id}.docx")

    if not os.path.exists(path):
        raise HTTPException(404, "File expired or not ready")

    background_tasks.add_task(cleanup_job, job_id)

    return FileResponse(
        path,
        filename="converted.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
