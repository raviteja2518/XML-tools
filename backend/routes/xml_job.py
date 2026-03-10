from fastapi import APIRouter, Body, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os, uuid, json, time, shutil

router = APIRouter()

BASE_DIR = "storage/jobs"
os.makedirs(BASE_DIR, exist_ok=True)

TTL_SECONDS = 60 * 60  # 1 hour

# ================= HELPERS =================

def job_dir(job_id: str):
    return os.path.join(BASE_DIR, job_id)

def cleanup_job(job_id: str):
    time.sleep(2)
    path = job_dir(job_id)
    if os.path.exists(path):
        shutil.rmtree(path)

# ================= CREATE JOB =================
@router.post("/xml/job/create")
def create_job(pages: dict = Body(...)):
    """
    pages = { "1": "page text", "2": "page text" }
    """
    job_id = str(uuid.uuid4())
    jd = job_dir(job_id)
    os.makedirs(jd, exist_ok=True)

    with open(f"{jd}/pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    with open(f"{jd}/annotations.json", "w") as f:
        json.dump({}, f)

    with open(f"{jd}/meta.json", "w") as f:
        json.dump(
            {
                "status": "created",
                "created_at": time.time()
            },
            f
        )

    return {"job_id": job_id, "total_pages": len(pages)}

# ================= GET PAGE =================
@router.get("/xml/job/{job_id}/page/{page_no}")
def get_page(job_id: str, page_no: int):
    path = f"{job_dir(job_id)}/pages.json"
    if not os.path.exists(path):
        raise HTTPException(404, "Job not found")

    pages = json.load(open(path, encoding="utf-8"))
    return {"page": page_no, "text": pages.get(str(page_no), "")}

# ================= SAVE TAG =================
@router.post("/xml/job/{job_id}/annotate")
def annotate(job_id: str, data: dict = Body(...)):
    """
    data = { page, start, end, tag, open, close }
    """
    jd = job_dir(job_id)
    ann_path = f"{jd}/annotations.json"

    annotations = json.load(open(ann_path)) if os.path.exists(ann_path) else {}
    page = str(data["page"])

    annotations.setdefault(page, []).append({
        "start": data["start"],
        "end": data["end"],
        "open": data.get("open", f"<{data['tag']}>"),
        "close": data.get("close", f"</{data['tag']}>")
    })

    with open(ann_path, "w") as f:
        json.dump(annotations, f, indent=2)

    return {"status": "saved"}

# ================= GENERATE XML =================
@router.post("/xml/job/{job_id}/generate")
def generate_xml(job_id: str):
    jd = job_dir(job_id)

    pages = json.load(open(f"{jd}/pages.json", encoding="utf-8"))
    annotations = json.load(open(f"{jd}/annotations.json"))

    xml = ["<document>"]

    for page_no, text in pages.items():
        page_text = text
        tags = annotations.get(page_no, [])

        # 🔥 Apply tags in reverse order (index safe)
        for t in sorted(tags, key=lambda x: x["start"], reverse=True):
            page_text = (
                page_text[:t["start"]] +
                t["open"] +
                page_text[t["start"]:t["end"]] +
                t["close"] +
                page_text[t["end"]:]
            )

        xml.append(f'  <page number="{page_no}">')
        xml.append(page_text)
        xml.append("  </page>")

    xml.append("</document>")

    out = f"{jd}/output.xml"
    open(out, "w", encoding="utf-8").write("\n".join(xml))

    # update meta
    meta_path = f"{jd}/meta.json"
    meta = json.load(open(meta_path))
    meta["status"] = "generated"
    json.dump(meta, open(meta_path, "w"), indent=2)

    return {"download": f"/xml/job/{job_id}/download"}

# ================= DOWNLOAD =================
@router.get("/xml/job/{job_id}/download")
def download(job_id: str, background_tasks: BackgroundTasks):
    path = f"{job_dir(job_id)}/output.xml"
    if not os.path.exists(path):
        raise HTTPException(404, "File not ready")

    background_tasks.add_task(cleanup_job, job_id)

    return FileResponse(
        path,
        media_type="application/xml",
        filename="output.xml"
    )
