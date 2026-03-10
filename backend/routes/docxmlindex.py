from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os, uuid, json, shutil
from PIL import Image
from services.docxmlindex_ocr import ocr_crop
from services.docxmlindex_xml import build_index_xml

router = APIRouter(prefix="/api/docxmlindex", tags=["DocXMLIndex"])
BASE_DIR = "temp_jobs"

@router.post("/upload-pages")
async def upload_pages(files: list[UploadFile] = File(...)):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(BASE_DIR, job_id)
    pages_dir = os.path.join(job_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    pages = []
    for i, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1].lower()
        unique_suffix = uuid.uuid4().hex[:6]
        base_name = f"page_{i+1:03}_{unique_suffix}"
        
        tiff_name = base_name + ext
        tiff_path = os.path.join(pages_dir, tiff_name)
        png_name = base_name + ".png"
        png_path = os.path.join(pages_dir, png_name)
        
        contents = await f.read()
        with open(tiff_path, "wb") as out: out.write(contents)
        
        # PNG preview for browser
        img = Image.open(tiff_path)
        img.save(png_path, "PNG")
        
        pages.append({
            "page": i+1, 
            "file": tiff_name, 
            "preview": f"http://localhost:8000/temp_jobs/{job_id}/pages/{png_name}"
        })

    with open(os.path.join(job_dir, "selections.json"), "w") as f:
        json.dump([], f)
    
    return {"job_id": job_id, "pages": pages}

@router.post("/save-selection")
async def save_selection(payload: dict):
    job_id = payload.get("job_id")
    job_dir = os.path.join(BASE_DIR, job_id)
    sel_file = os.path.join(job_dir, "selections.json")
    
    data = []
    if os.path.exists(sel_file):
        with open(sel_file, "r") as f: data = json.load(f)

    data.append(payload)
    with open(sel_file, "w") as f: json.dump(data, f, indent=2)
    return {"status": "saved", "count": len(data)}

@router.post("/generate-xml")
def generate_xml(job_id: str):
    job_dir = os.path.join(BASE_DIR, job_id)
    sel_file = os.path.join(job_dir, "selections.json")
    
    with open(sel_file) as f: selections = json.load(f)

    all_text_blocks = []
    for sel in selections:
        img_path = os.path.join(job_dir, "pages", sel["file"])
        if os.path.exists(img_path):
            text = ocr_crop(img_path, sel)
            if text.strip(): all_text_blocks.append(text)

    final_xml = build_index_xml(all_text_blocks)
    xml_path = os.path.join(job_dir, "index.xml")
    with open(xml_path, "w", encoding="utf-8") as f: f.write(final_xml)
    return {"status": "ready"}

@router.get("/download")
def download_xml(job_id: str):
    xml_path = os.path.join(BASE_DIR, job_id, "index.xml")
    return FileResponse(xml_path, filename="index.xml")