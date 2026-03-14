from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pdfminer.high_level import extract_text
import xml.etree.ElementTree as ET
import uuid, os, re, time

router = APIRouter()

TEMP_DIR = "storage/temp"
TTL = 1800

os.makedirs(TEMP_DIR, exist_ok=True)


# ---------------- CLEAN TEXT ----------------

def clean_text(text):

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("Bibliography", "")

    return text.strip()


# ---------------- SPLIT REFERENCES ----------------

def split_refs(text):

    refs = re.split(r"\.\s(?=[A-Z][a-zA-Z\-]+,\s)", text)

    refs = [r.strip()+"." for r in refs if len(r.strip()) > 30]

    return refs


# ---------------- PARSE AUTHORS ----------------

def parse_authors(text, parent):

    authors_block = ET.SubElement(parent, "ref-authors")

    pattern = r"([A-Z][a-zA-Z\-]+),\s([A-Z][a-zA-Z\-]+)"

    matches = re.findall(pattern, text)

    if not matches:
        return

    for i, (surname, given) in enumerate(matches):

        author = ET.SubElement(authors_block, "author", seq=str(i+1))

        ET.SubElement(author, "ce:initials").text = given[0] + "."
        ET.SubElement(author, "ce:surname").text = surname
        ET.SubElement(author, "ce:given-name").text = given


# ---------------- PARSE YEAR ----------------

def parse_year(text, parent):

    year_match = re.search(r"\b(19|20)\d{2}\b", text)

    year_tag = ET.SubElement(parent, "ref-publicationyear")

    if year_match:
        year_tag.set("first", year_match.group())


# ---------------- PARSE TITLE ----------------

def parse_title(text, parent):

    title_block = ET.SubElement(parent, "ref-title")
    title_text = ET.SubElement(title_block, "ref-titletext-english")

    match = re.search(r"\d{4}\.\s(.+?)\.\s[A-Z]", text)

    if match:
        title_text.text = match.group(1).strip()


# ---------------- PARSE SOURCE ----------------

def parse_source(text, parent):

    source = ET.SubElement(parent, "ref-sourcetitle")

    match = re.search(r"\.\s([A-Z][A-Za-z\s]+)\s\d", text)

    if match:
        source.text = match.group(1).strip()


# ---------------- PARSE VOLUME ISSUE ----------------

def parse_volume_issue(text, parent):

    volisspag = ET.SubElement(parent, "volisspag")

    vol_issue = ET.SubElement(volisspag, "volume-issue-number")

    vol_match = re.search(r"(\d+)\((\d+)\)", text)

    if vol_match:

        ET.SubElement(vol_issue, "vol-first").text = vol_match.group(1)
        ET.SubElement(vol_issue, "iss-first").text = vol_match.group(2)


# ---------------- PARSE PAGES ----------------

def parse_pages(text, parent):

    volisspag = parent.find("volisspag")

    if volisspag is None:
        volisspag = ET.SubElement(parent, "volisspag")

    page_info = ET.SubElement(volisspag, "page-information")
    pages = ET.SubElement(page_info, "pages")

    match = re.search(r":\s*(\d+)[-–](\d+)", text)

    if match:

        ET.SubElement(pages, "first-page").text = match.group(1)
        ET.SubElement(pages, "last-page").text = match.group(2)


# ---------------- PARSE REF TEXT ----------------

def parse_ref_text(text, parent):

    ref_text = ET.SubElement(parent, "ref-text")

    match = re.search(r"\)\.\s(.+)", text)

    if match:
        ref_text.text = match.group(1).strip()


# ---------------- BUILD REFERENCE ----------------

def build_reference(text, seq):

    reference = ET.Element("reference", seq=str(seq))

    ref_info = ET.SubElement(reference, "ref-info")

    parse_title(text, ref_info)
    parse_authors(text, ref_info)
    parse_source(text, ref_info)
    parse_year(text, ref_info)
    parse_volume_issue(text, ref_info)
    parse_pages(text, ref_info)
    parse_ref_text(text, ref_info)

    ET.SubElement(reference, "ref-fulltext").text = text
    ET.SubElement(reference, "ce:source-text").text = text

    return reference


# ---------------- BUILD XML ----------------

def build_xml(refs):

    tail = ET.Element("tail")

    bibliography = ET.SubElement(tail, "bibilography")

    for i, ref in enumerate(refs, 1):

        node = build_reference(ref, i)

        bibliography.append(node)

    return tail


# ---------------- CLEANUP ----------------

def cleanup(path):

    time.sleep(TTL)

    if os.path.exists(path):
        os.remove(path)


# ---------------- UPLOAD ----------------

@router.post("/api/tail/upload")

async def upload_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())

    pdf_path = f"{TEMP_DIR}/{job_id}.pdf"
    xml_path = f"{TEMP_DIR}/{job_id}.xml"

    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(pdf_path)

    text = clean_text(text)

    refs = split_refs(text)

    xml_root = build_xml(refs)

    tree = ET.ElementTree(xml_root)

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    background_tasks.add_task(cleanup, pdf_path)
    background_tasks.add_task(cleanup, xml_path)

    return {"job_id": job_id}


# ---------------- DOWNLOAD ----------------

@router.get("/api/tail/download/{job_id}")

def download_xml(job_id: str):

    xml_path = f"{TEMP_DIR}/{job_id}.xml"

    if not os.path.exists(xml_path):
        raise HTTPException(404, "File expired")

    return FileResponse(
        xml_path,
        filename="tail_references.xml",
        media_type="application/xml"
    )