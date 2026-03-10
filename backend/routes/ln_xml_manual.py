from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import os
import time
import threading

router = APIRouter()

BASE_DIR = "storage/lnxml"
os.makedirs(BASE_DIR, exist_ok=True)

TTL_SECONDS = 30 * 60  # 30 minutes


# ===============================
# 🔥 CLEANUP HELPERS
# ===============================
def safe_delete(path: str):
    time.sleep(2)  # ensure download completes
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Cleanup error: {e}")


def ttl_cleanup_worker():
    while True:
        now = time.time()
        for file in os.listdir(BASE_DIR):
            path = os.path.join(BASE_DIR, file)
            try:
                if os.path.isfile(path):
                    if now - os.path.getctime(path) > TTL_SECONDS:
                        os.remove(path)
            except Exception:
                pass
        time.sleep(300)  # run every 5 mins


# 🔁 Start TTL cleaner once (on app start)
threading.Thread(target=ttl_cleanup_worker, daemon=True).start()


# ===============================
# XML TEMPLATE
# ===============================
XML_TEMPLATE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE COURTCASE PUBLIC "//LN//COURTCASEv06-000//EN" "/xhccs/bin/COURTCASE-v6-NORM.dtd">
<COURTCASE>
<lndocmeta:docinfo>
<lndocmeta:lnlni lnlni=""/>
<lndocmeta:lnminrev lnminrev="00000"/>
<lndocmeta:smi lnsmi="6GNC"/>
<lndocmeta:dpsi lndpsi="J4P0"/>
<lndocmeta:lnsourcedocid lnsourcedocid=""/>
<lndocmeta:lndoctype lndoctypename="COURTCASE"/>
<lndocmeta:lndoctypeversion lndoctypeversionmajor="06" lndoctypeversionminor="000"/>
<lndocmeta:lndoctypelang lndoctypelang="EN"/>
<lndocmeta:lnfilenum lnfilenum="077"/>
<lndocmeta:fabinfo>
<lndocmeta:fabinfoitem name="B4DBNO" value="1MXQ"/>
</lndocmeta:fabinfo>
</lndocmeta:docinfo>
"""

CLOSE_TAG = "\n</COURTCASE>"


# ===============================
# MANUAL XML UPLOAD
# ===============================
@router.post("/ln-xml/manual-upload")
async def manual_xml_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(status_code=400, detail="Only XML files allowed")

    content = (await file.read()).decode("utf-8", errors="ignore")

    # Remove XML declaration & root if exists
    cleaned = content
    cleaned = cleaned.replace('<?xml version="1.0" encoding="ISO-8859-1"?>', "")
    cleaned = cleaned.replace("<COURTCASE>", "")
    cleaned = cleaned.replace("</COURTCASE>", "")
    cleaned = cleaned.strip()

    final_xml = XML_TEMPLATE + "\n" + cleaned + CLOSE_TAG

    job_id = str(uuid.uuid4())
    output_path = os.path.join(BASE_DIR, f"{job_id}.xml")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_xml)

    return {
        "download_url": f"/ln-xml/manual-download/{job_id}"
    }


# ===============================
# DOWNLOAD + AUTO DELETE
# ===============================
@router.get("/ln-xml/manual-download/{job_id}")
def download_xml(job_id: str, background_tasks: BackgroundTasks):
    path = os.path.join(BASE_DIR, f"{job_id}.xml")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File expired or not found")

    # 🔥 delete after download
    background_tasks.add_task(safe_delete, path)

    return FileResponse(
        path,
        media_type="application/xml",
        filename="LN_COURTCASE.xml"
    )
