from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from lxml import etree
import uuid, os, time, shutil, threading

router = APIRouter(prefix="/bits")

BASE_DIR = "storage/bits_jobs"
TTL_SECONDS = 30 * 60  # 30 mins

os.makedirs(BASE_DIR, exist_ok=True)

# ================= TTL CLEANER =================
def ttl_cleanup():
    while True:
        now = time.time()
        for job_id in os.listdir(BASE_DIR):
            path = os.path.join(BASE_DIR, job_id)
            if os.path.isdir(path):
                if now - os.path.getctime(path) > TTL_SECONDS:
                    shutil.rmtree(path, ignore_errors=True)
        time.sleep(300)

threading.Thread(target=ttl_cleanup, daemon=True).start()

# ================= UTIL =================
def safe_text(el):
    return el.text.strip() if el is not None and el.text else ""

def parse_pub_date(text):
    # Example: "23 Jan 2018"
    parts = text.split()
    return {
        "day": parts[0],
        "month": time.strptime(parts[1], "%b").tm_mon,
        "year": parts[2]
    }

# ================= API =================
@router.post("/meta/upload")
async def upload_meta_xml(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(400, "XML only")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    in_path = os.path.join(job_dir, "input.xml")
    out_path = os.path.join(job_dir, "output.xml")

    with open(in_path, "wb") as f:
        f.write(await file.read())

    tree = etree.parse(in_path)
    root = tree.getroot()

    # ================= EXTRACT =================
    title = root.findtext(".//Title")
    series = root.findtext(".//Series_Title")
    esibn = root.findtext(".//EISBN")

    bisac = [e.text for e in root.findall(".//BISAC_Subject_1_code")]
    bic = [e.text for e in root.findall(".//BIC_Subject_1_code")]
    thema = [e.text for e in root.findall(".//Thema_Subject_2_code")]

    pub_raw = root.findtext(".//Publication_Date")
    pub = parse_pub_date(pub_raw)

    short_desc = root.findtext(".//Short_Description")
    main_desc = root.findtext(".//Main_Description")

    lname = root.findtext(".//Contributor_1_Last_name")
    fname = root.findtext(".//Contributor_1_First_name")

    hb_isbn = root.findtext(".//Hardback_ISBN")
    pr_isbn = root.findtext(".//Print_ISBN")
    epub_isbn = root.findtext(".//EPUB_ISBN")

    # ================= BUILD BITS XML =================
    B = etree.Element("book")

    meta = etree.SubElement(B, "book-meta")

    etree.SubElement(meta, "book-id", {"book-id-type": "doi"}).text = f"10.1108/{esibn}"

    for grp, items in {
        "bisac": bisac,
        "bic": bic,
        "thema": thema,
    }.items():
        sg = etree.SubElement(meta, "subj-group", {"subj-group-type": grp})
        for v in items:
            etree.SubElement(sg, "subject").text = v

    btg = etree.SubElement(meta, "book-title-group")
    etree.SubElement(btg, "book-title").text = title
    etree.SubElement(btg, "alt-title", {"alt-title-type": "short-name"}).text = esibn

    cg = etree.SubElement(meta, "contrib-group")
    c = etree.SubElement(cg, "contrib", {"contrib-type": "editor"})
    n = etree.SubElement(c, "name")
    etree.SubElement(n, "surname").text = lname
    etree.SubElement(n, "given-names").text = fname

    for fmt in ["electronic", "print"]:
        pd = etree.SubElement(meta, "pub-date", {
            "publication-format": fmt,
            "date-type": "pub",
            "iso-8601-date": pub_raw
        })
        etree.SubElement(pd, "day").text = pub["day"]
        etree.SubElement(pd, "month").text = str(pub["month"])
        etree.SubElement(pd, "year").text = pub["year"]

    etree.SubElement(meta, "isbn", {"publication-format": "electronic"}).text = esibn
    etree.SubElement(meta, "isbn", {"publication-format": "hardback"}).text = hb_isbn
    etree.SubElement(meta, "isbn", {"publication-format": "paperback"}).text = pr_isbn
    etree.SubElement(meta, "isbn", {"publication-format": "epub"}).text = epub_isbn

    abs1 = etree.SubElement(meta, "abstract", {
        "abstract-type": "precis",
        "id": f"book-{esibn}-abstract1"
    })
    etree.SubElement(abs1, "p").text = short_desc

    abs2 = etree.SubElement(meta, "abstract", {
        "abstract-type": "abstract",
        "id": f"book-{esibn}-abstract2"
    })
    etree.SubElement(abs2, "p").text = main_desc

    cmg = etree.SubElement(meta, "custom-meta-group")
    cm = etree.SubElement(cmg, "custom-meta")
    etree.SubElement(cm, "meta-name").text = "publication-status"
    etree.SubElement(cm, "meta-value").text = "available"

    etree.ElementTree(B).write(
        out_path,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )

    return {
        "job_id": job_id,
        "download": f"/bits/meta/download/{job_id}"
    }

# ================= DOWNLOAD =================
@router.get("/meta/download/{job_id}")
def download(job_id: str, background_tasks: BackgroundTasks):
    job_dir = os.path.join(BASE_DIR, job_id)
    path = os.path.join(job_dir, "output.xml")

    if not os.path.exists(path):
        raise HTTPException(404, "Expired")

    background_tasks.add_task(shutil.rmtree, job_dir, True)

    return FileResponse(path, filename="bits.xml", media_type="application/xml")
