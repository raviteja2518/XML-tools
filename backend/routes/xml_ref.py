from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
import uuid, os, threading, time

from services.docx_parser import extract_references
from services.ref_parser import parse_reference
from services.xml_refbuilder import build_ref_list_xml
from services.cleanup import schedule_cleanup

xml_ref_router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@xml_ref_router.post("/upload")
async def upload_docx(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx allowed")

    uid = str(uuid.uuid4())
    upload_path = f"{UPLOAD_DIR}/{uid}.docx"

    with open(upload_path, "wb") as f:
        f.write(await file.read())

    raw_refs = extract_references(upload_path)

    if not raw_refs:
        raise HTTPException(status_code=400, detail="No references found")

    parsed_refs = [parse_reference(r) for r in raw_refs]

    xml_path = build_ref_list_xml(parsed_refs, uid)

    os.remove(upload_path)

    background_tasks.add_task(schedule_cleanup, xml_path, 1800)

    return {
        "xml_file": xml_path,
        "ref_count": len(parsed_refs)
    }


@xml_ref_router.get("/download")
def download_xml(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File expired")

    response = FileResponse(
        path,
        media_type="application/octet-stream",
        filename="references.xml"
    )

    def cleanup():
        time.sleep(1)
        if os.path.exists(path):
            os.remove(path)

    threading.Thread(target=cleanup, daemon=True).start()
    return response
