from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
from PIL import Image
import pytesseract
import os, uuid, time, threading, shutil
from docx import Document
from bs4 import BeautifulSoup

router = APIRouter()

# ================= CONFIG =================
BASE_DIR = "storage/ocr_clean"
ENTITY_FILE = "data/entities.html"
TTL_SECONDS = 30 * 60

os.makedirs(BASE_DIR, exist_ok=True)

# ================= ENTITY MAP =================
def load_entities():
    if not os.path.exists(ENTITY_FILE):
        return {}

    soup = BeautifulSoup(open(ENTITY_FILE, encoding="utf-8"), "html.parser")
    table = soup.find("table")
    mapping = {}

    if table:
        for row in table.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                symbol = cols[-1].text.strip()
                hexval = cols[-2].text.strip()
                # exclude common punctuation
                if symbol not in [".", ","]:
                    mapping[symbol] = hexval
    return mapping

ENTITY_MAP = load_entities()

def apply_entities(text: str) -> str:
    return "".join(ENTITY_MAP.get(ch, ch) for ch in text)

# ================= OCR (LAYOUT SAFE) =================
def ocr_image(img: Image.Image) -> str:
    raw = pytesseract.image_to_string(
        img,
        lang="eng",
        config="--oem 3 --psm 4"
    )

    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            # paragraph break
            lines.append("")
        else:
            lines.append(line)

    # rebuild paragraphs (no forced line breaks)
    paragraphs = []
    buffer = []

    for ln in lines:
        if ln == "":
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
        else:
            buffer.append(ln)

    if buffer:
        paragraphs.append(" ".join(buffer))

    final_text = "\n\n".join(paragraphs)
    return apply_entities(final_text)

# ================= OCR JOB =================
def run_ocr(job_id: str, tiff_files: List[str]):
    job_dir = os.path.join(BASE_DIR, job_id)
    out_doc = os.path.join(job_dir, "output.docx")

    doc = Document()

    for idx, path in enumerate(tiff_files, start=1):
        img = Image.open(path)
        text = ocr_image(img)

        # 🔥 EXACT 1 PAGE PER IMAGE
        if idx > 1:
            doc.add_page_break()

        doc.add_paragraph(text)

    doc.save(out_doc)

# ================= CLEANUP =================
def delete_job(job_dir: str):
    time.sleep(2)
    shutil.rmtree(job_dir, ignore_errors=True)

def ttl_cleanup_worker():
    while True:
        now = time.time()
        for job_id in os.listdir(BASE_DIR):
            path = os.path.join(BASE_DIR, job_id)
            try:
                if os.path.isdir(path) and now - os.path.getctime(path) > TTL_SECONDS:
                    shutil.rmtree(path, ignore_errors=True)
            except:
                pass
        time.sleep(300)

threading.Thread(target=ttl_cleanup_worker, daemon=True).start()

# ================= API =================
@router.post("/ocr/process")
async def process_ocr(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "No TIFF files uploaded")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    tiff_paths = []

    for i, f in enumerate(sorted(files, key=lambda x: x.filename), start=1):
        if not f.filename.lower().endswith((".tif", ".tiff")):
            raise HTTPException(400, "Only TIFF files allowed")

        path = os.path.join(job_dir, f"page_{i}.tiff")
        with open(path, "wb") as out:
            out.write(await f.read())
        tiff_paths.append(path)

    run_ocr(job_id, tiff_paths)

    return {
        "job_id": job_id,
        "download_url": f"/ocr/download/{job_id}"
    }

@router.get("/ocr/download/{job_id}")
def download(job_id: str, bg: BackgroundTasks):
    job_dir = os.path.join(BASE_DIR, job_id)
    path = os.path.join(job_dir, "output.docx")

    if not os.path.exists(path):
        raise HTTPException(404, "File expired")

    bg.add_task(delete_job, job_dir)

    return FileResponse(
        path,
        filename="ocr_output.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
