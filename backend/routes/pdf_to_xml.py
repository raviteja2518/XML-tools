from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os, uuid, threading, json, time, shutil

from services.ocr_service import ocr_pdf
from services.entity_service import replace_entities
from services.xml_builder import build_book_xml

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JOB_DIR = os.path.join(BASE_DIR, "storage", "jobs")
OUT_DIR = os.path.join(BASE_DIR, "storage", "output")
PROGRESS_DIR = os.path.join(BASE_DIR, "storage", "progress")

os.makedirs(JOB_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PROGRESS_DIR, exist_ok=True)

TTL_SECONDS = 30 * 60  # 30 minutes


# ===============================
# 🔥 HELPERS
# ===============================
def write_progress(job_id: str, val: int):
    with open(os.path.join(PROGRESS_DIR, f"{job_id}.json"), "w") as f:
        json.dump(
            {"progress": val, "created_at": time.time()},
            f
        )


def delete_job(job_id: str):
    time.sleep(2)  # ensure download completes

    pdf_path = os.path.join(JOB_DIR, f"{job_id}.pdf")
    xml_path = os.path.join(OUT_DIR, f"{job_id}.xml")
    progress_path = os.path.join(PROGRESS_DIR, f"{job_id}.json")

    try:
        for p in [pdf_path, xml_path, progress_path]:
            if os.path.exists(p):
                os.remove(p)
    except Exception as e:
        print("Cleanup error:", e)


def ttl_cleanup_worker():
    while True:
        now = time.time()

        for f in os.listdir(PROGRESS_DIR):
            if not f.endswith(".json"):
                continue

            path = os.path.join(PROGRESS_DIR, f)
            try:
                data = json.load(open(path))
                created = data.get("created_at", now)
                job_id = f.replace(".json", "")

                if now - created > TTL_SECONDS:
                    delete_job(job_id)

            except Exception:
                pass

        time.sleep(300)  # every 5 mins


# 🔁 Start TTL cleaner once
threading.Thread(target=ttl_cleanup_worker, daemon=True).start()


# ===============================
# WORKER THREAD
# ===============================
def process_pdf(job_id: str, pdf_path: str):
    try:
        write_progress(job_id, 5)

        pages = ocr_pdf(pdf_path)
        write_progress(job_id, 40)

        pages = [replace_entities(p) for p in pages]
        write_progress(job_id, 70)

        xml = build_book_xml(pages)
        write_progress(job_id, 90)

        out = os.path.join(OUT_DIR, f"{job_id}.xml")
        open(out, "w", encoding="utf-8").write(xml)

        write_progress(job_id, 100)

    except Exception as e:
        print("❌ Processing failed:", e)
        write_progress(job_id, 100)


# ===============================
# API
# ===============================
@router.post("/tools/pdf-to-xml")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())
    pdf_path = os.path.join(JOB_DIR, f"{job_id}.pdf")

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    threading.Thread(
        target=process_pdf,
        args=(job_id, pdf_path),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "download": f"/tools/download-xml/{job_id}",
        "progress": f"/tools/progress/{job_id}"
    }


@router.get("/tools/progress/{job_id}")
def progress(job_id: str):
    p = os.path.join(PROGRESS_DIR, f"{job_id}.json")
    if not os.path.exists(p):
        return {"status": "expired"}
    return json.load(open(p))


# ===============================
# DOWNLOAD + AUTO DELETE
# ===============================
@router.get("/tools/download-xml/{job_id}")
def download_xml(job_id: str, background_tasks: BackgroundTasks):
    path = os.path.join(OUT_DIR, f"{job_id}.xml")

    if not os.path.exists(path):
        raise HTTPException(404, "File expired or not found")

    # 🔥 delete everything after download
    background_tasks.add_task(delete_job, job_id)

    return FileResponse(
        path,
        media_type="application/xml",
        filename="output.xml"
    )
