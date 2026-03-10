from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import threading, os, time

from services.case_file_handler import save_upload, output_path
from services.case_docx_parser import extract_text_from_docx
from services.case_pdf_parser import extract_text_from_pdf
from services.case_xml_builder import build_ref_list_xml
from services.case_cleanup import schedule_delete, delete_file
from services.case_case_parser import parse_case   # ✅ correct parser

case_reference_router = APIRouter(
    prefix="/api/case-reference",
    tags=["Case Reference"]
)

# ================= UPLOAD =================
@case_reference_router.post("/upload")
async def upload_case_file(
    file: UploadFile = File(...),
    bg: BackgroundTasks = BackgroundTasks()   # ✅ always available
):
    # ---------- validate file ----------
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx"):
        raise HTTPException(400, "Only PDF or DOCX allowed")

    # ---------- save upload ----------
    job_id, upload_path = save_upload(await file.read(), ext)

    try:
        # ---------- extract text ----------
        if ext == "pdf":
            text = extract_text_from_pdf(upload_path)
        else:
            text = extract_text_from_docx(upload_path)

        if not text or len(text.strip()) < 20:
            raise HTTPException(400, "No readable text found in file")

        # ---------- parse case (NOT references) ----------
        case_data = parse_case(text)

        # ---------- build XML ----------
        xml_path = build_ref_list_xml(case_data, job_id)

    except HTTPException:
        delete_file(upload_path)
        raise
    except Exception as e:
        delete_file(upload_path)
        raise HTTPException(500, f"Processing failed: {str(e)}")

    # ---------- delete uploaded file immediately ----------
    delete_file(upload_path)

    # ---------- auto delete XML after 30 mins if not downloaded ----------
    bg.add_task(schedule_delete, xml_path, 1800)

    # ---------- preview for FE editor ----------
    with open(xml_path, "r", encoding="utf-8") as f:
        preview = f.read()

    return {
        "job_id": job_id,
        "preview_xml": preview
    }

# ================= UPDATE =================
@case_reference_router.post("/update")
def update_xml(data: dict):
    job_id = data.get("job_id")
    xml = data.get("xml")

    if not job_id or not xml:
        raise HTTPException(400, "Invalid update payload")

    path = output_path(job_id)
    if not os.path.exists(path):
        raise HTTPException(404, "File expired or deleted")

    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)

    return {"status": "updated"}

# ================= DOWNLOAD =================
@case_reference_router.get("/download")
def download_xml(job_id: str):
    path = output_path(job_id)
    if not os.path.exists(path):
        raise HTTPException(404, "File expired or deleted")

    # ---------- delete after download ----------
    def cleanup():
        time.sleep(1)
        delete_file(path)

    threading.Thread(target=cleanup, daemon=True).start()

    return FileResponse(
        path=path,
        media_type="application/octet-stream",
        filename="case.xml"
    )
