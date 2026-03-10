from fastapi import APIRouter, UploadFile, File, Body, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from docx import Document
import os, uuid, json, time, shutil, threading

router = APIRouter()

BASE_DIR = "storage/ln_jobs"
TTL_SECONDS = 30 * 60  # 30 minutes

os.makedirs(BASE_DIR, exist_ok=True)

# ===============================
# CLEANUP HELPERS
# ===============================

def delete_job_dir(job_dir: str):
    time.sleep(2)  # allow download finish
    if os.path.exists(job_dir):
        shutil.rmtree(job_dir, ignore_errors=True)
        print("🧹 Job cleaned:", job_dir)


def ttl_cleanup_worker():
    while True:
        now = time.time()
        for job_id in os.listdir(BASE_DIR):
            job_dir = os.path.join(BASE_DIR, job_id)
            try:
                if os.path.isdir(job_dir):
                    if now - os.path.getctime(job_dir) > TTL_SECONDS:
                        shutil.rmtree(job_dir, ignore_errors=True)
                        print("⏰ TTL cleanup:", job_id)
            except Exception:
                pass
        time.sleep(300)  # every 5 min


threading.Thread(target=ttl_cleanup_worker, daemon=True).start()

# ===============================
# DOCX → PAGE SPLIT
# ===============================

def split_docx_into_pages(docx_path: str):
    doc = Document(docx_path)
    pages = []
    current = []

    for para in doc.paragraphs:
        for run in para.runs:
            if run._element.xpath('.//w:br[@w:type="page"]'):
                pages.append("\n".join(current))
                current = []
        if para.text.strip():
            current.append(para.text)

    if current:
        pages.append("\n".join(current))

    return pages or [""]

# ===============================
# UPLOAD
# ===============================

@router.post("/lnxml/upload")
async def upload_word(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Only .docx allowed")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    path = os.path.join(job_dir, "input.docx")
    with open(path, "wb") as f:
        f.write(await file.read())

    pages = split_docx_into_pages(path)

    json.dump(pages, open(f"{job_dir}/pages.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    json.dump({}, open(f"{job_dir}/tags.json", "w", encoding="utf-8"), indent=2)

    return {"job_id": job_id, "pages": pages}

# ===============================
# SAVE TAG (SAFE)
# ===============================

@router.post("/lnxml/tag")
def save_tag(data: dict = Body(...)):
    required = {"job_id", "page", "start", "end", "tag", "open", "close"}
    if not required.issubset(data.keys()):
        raise HTTPException(400, "Invalid tag payload")

    job_dir = os.path.join(BASE_DIR, data["job_id"])
    tags_path = os.path.join(job_dir, "tags.json")

    if not os.path.exists(tags_path):
        raise HTTPException(409, "Job expired or already generated")

    tags = json.load(open(tags_path, encoding="utf-8"))

    page = str(data["page"])
    tags.setdefault(page, []).append({
        "start": data["start"],
        "end": data["end"],
        "tag": data["tag"],
        "open": data["open"],
        "close": data["close"],
    })

    json.dump(tags, open(tags_path, "w", encoding="utf-8"), indent=2)
    return {"status": "ok"}

# ===============================
# GENERATE XML
# ===============================

@router.post("/lnxml/generate")
def generate_xml(job_id: str = Body(..., embed=True)):
    job_dir = os.path.join(BASE_DIR, job_id)
    if not os.path.exists(job_dir):
        raise HTTPException(404, "Job expired")

    pages = json.load(open(f"{job_dir}/pages.json", encoding="utf-8"))
    tags = json.load(open(f"{job_dir}/tags.json", encoding="utf-8"))

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', "<COURTCASE>"]

    for i, page_text in enumerate(pages, start=1):
        page_tags = tags.get(str(i), [])
        text = page_text

        for t in sorted(page_tags, key=lambda x: x["start"], reverse=True):
            text = (
                text[:t["start"]] +
                t["open"] +
                text[t["start"]:t["end"]] +
                t["close"] +
                text[t["end"]:]
            )

        xml.append(text)

    xml.append("</COURTCASE>")

    out_path = f"{job_dir}/output.xml"
    open(out_path, "w", encoding="utf-8").write("\n".join(xml))

    return {"download": f"/lnxml/download/{job_id}"}

# ===============================
# DOWNLOAD + AUTO DELETE
# ===============================

@router.get("/lnxml/download/{job_id}")
def download_xml(job_id: str, background_tasks: BackgroundTasks):
    job_dir = os.path.join(BASE_DIR, job_id)
    path = os.path.join(job_dir, "output.xml")

    if not os.path.exists(path):
        raise HTTPException(404, "File expired")

    background_tasks.add_task(delete_job_dir, job_dir)

    return FileResponse(
        path,
        media_type="application/xml",
        filename="ln.xml"
    )
