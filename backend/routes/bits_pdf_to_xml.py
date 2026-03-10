from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from lxml import etree
from pdf2image import convert_from_path, pdfinfo_from_path
import pytesseract
import uuid, os, time, threading, shutil

router = APIRouter()

BASE_TMP = "tmp/jobs"
TTL_SECONDS = 30 * 60  # 30 minutes

os.makedirs(BASE_TMP, exist_ok=True)

progress_map = {}
job_created_at = {}

# ---------------- CLEANUP WORKER ----------------
def cleanup_worker():
    while True:
        now = time.time()
        for job_id in list(job_created_at.keys()):
            if now - job_created_at[job_id] > TTL_SECONDS:
                job_dir = os.path.join(BASE_TMP, job_id)
                shutil.rmtree(job_dir, ignore_errors=True)
                progress_map.pop(job_id, None)
                job_created_at.pop(job_id, None)
        time.sleep(60)

threading.Thread(target=cleanup_worker, daemon=True).start()

# ---------------- PROCESS PDF ----------------
def process_pdf(job_id, pdf_path, xml_path):
    progress_map[job_id] = 0

    # ✅ TOTAL PAGES
    info = pdfinfo_from_path(pdf_path)
    total_pages = info["Pages"]

    root = etree.Element("book")
    body = etree.SubElement(root, "book-body")
    part = etree.SubElement(body, "book-part", attrib={"book-part-type": "chapter"})
    body_tag = etree.SubElement(part, "body")

    for page in range(1, total_pages + 1):
        images = convert_from_path(
            pdf_path,
            dpi=300,
            first_page=page,
            last_page=page
        )

        img = images[0]
        text = pytesseract.image_to_string(img)

        p = etree.SubElement(body_tag, "p")
        p.text = text.strip()

        percent = int((page / total_pages) * 80)
        progress_map[job_id] = percent
        time.sleep(0.2)

    # ---- Dummy Reference (later enhance) ----
    ref_list = etree.SubElement(root, "ref-list")
    ref = etree.SubElement(ref_list, "ref")
    mc = etree.SubElement(ref, "mixed-citation", publication_type="journal")
    etree.SubElement(mc, "article-title").text = "Detected Reference"
    etree.SubElement(mc, "year").text = "2024"

    progress_map[job_id] = 100

    etree.ElementTree(root).write(
        xml_path,
        pretty_print=True,
        encoding="UTF-8",
        xml_declaration=True
    )

# ---------------- UPLOAD API ----------------
@router.post("/bits/pdf-to-xml")
async def upload_pdf(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_TMP, job_id)
    os.makedirs(job_dir, exist_ok=True)

    pdf_path = os.path.join(job_dir, "input.pdf")
    xml_path = os.path.join(job_dir, "output.xml")

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    job_created_at[job_id] = time.time()
    progress_map[job_id] = 0

    threading.Thread(
        target=process_pdf,
        args=(job_id, pdf_path, xml_path),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "progress_url": f"/bits/progress/{job_id}",
        "download_url": f"/bits/download/{job_id}"
    }

# ---------------- SSE PROGRESS ----------------
@router.get("/bits/progress/{job_id}")
def progress_sse(job_id: str):
    def stream():
        last = -1
        while True:
            val = progress_map.get(job_id, 0)
            if val != last:
                yield f"data: {val}\n\n"
                last = val
            if val >= 100:
                break
            time.sleep(1)

    return StreamingResponse(stream(), media_type="text/event-stream")

# ---------------- DOWNLOAD (AUTO DELETE) ----------------
@router.get("/bits/download/{job_id}")
def download_xml(job_id: str):
    job_dir = os.path.join(BASE_TMP, job_id)
    xml_path = os.path.join(job_dir, "output.xml")

    if not os.path.exists(xml_path):
        return {"error": "File expired"}

    def cleanup():
        time.sleep(5)  # allow browser to finish download
        shutil.rmtree(job_dir, ignore_errors=True)
        progress_map.pop(job_id, None)
        job_created_at.pop(job_id, None)

    threading.Thread(target=cleanup, daemon=True).start()

    return FileResponse(
        xml_path,
        filename="bits.xml",
        media_type="application/xml"
    )
