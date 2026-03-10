import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from routes import pdf_to_tiff
from routes import pdf_to_word
from routes import pdf_split
from routes import ocr_preview
from routes.ln_xml import router as ln_xml_router
from routes.xml_job import router
from routes.folder_creator import router as folder_router
from routes import ln_xml_manual
from routes import image_crop
from routes.pdf_to_word_ocr import router as ocr_router
from routes.ws_progress import router as ws_router
from routes.pdf_to_xml import router
from routes.bits_pdf_to_xml import router as bits_router
from routes.split_pdf import router as split_pdf_router
from routes.bits_meta import router as bits_meta_router
from routes.xml_ref import xml_ref_router
from routes.case_reference import case_reference_router
from routes.build import router as build_router
from routes.ocr_docbook import router as ocr_docbook_router
from routes.docxmlindex import router as docxmlindex_router
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# ✅ CORS (TEMP – for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routes
app.include_router(pdf_to_word.router)

# ✅ Serve output files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.include_router(pdf_to_tiff.router)
app.include_router(pdf_split.router)
app.include_router(ocr_preview.router)
app.include_router(ln_xml_router)
app.include_router(router)
app.include_router(folder_router)
app.include_router(ln_xml_manual.router)
app.include_router(image_crop.router)
app.include_router(ocr_router)
app.include_router(ws_router)
app.include_router(router)
app.include_router(bits_router)
app.include_router(split_pdf_router)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/temp_jobs", StaticFiles(directory="temp_jobs"), name="temp_jobs")
app.include_router(xml_ref_router, prefix="/api/xml-ref")
app.include_router(case_reference_router)
app.include_router(build_router)
app.include_router(ocr_docbook_router)
app.include_router(docxmlindex_router)
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Setup Base Directory for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. Initialize FastAPI
app = FastAPI(title="Black Vave Multi-Tool API")

# 3. CORS Middleware (Essential for Frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Static File Mounting 
# Move these ABOVE routes to ensure they are registered before any requests hit
os.makedirs("outputs", exist_ok=True)
os.makedirs("temp_jobs", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/temp_jobs", StaticFiles(directory="temp_jobs"), name="temp_jobs")

# 5. Import Routers
from routes import (
    pdf_to_tiff, pdf_to_word, pdf_split, ocr_preview, 
    ln_xml_manual, image_crop, pdf_to_xml, split_pdf
)
from routes.ln_xml import router as ln_xml_router
from routes.xml_job import router as xml_job_router
from routes.folder_creator import router as folder_router
from routes.pdf_to_word_ocr import router as ocr_router
from routes.ws_progress import router as ws_router
from routes.bits_pdf_to_xml import router as bits_router
from routes.bits_meta import router as bits_meta_router
from routes.xml_ref import xml_ref_router
from routes.case_reference import case_reference_router
from routes.build import router as build_router
from routes.ocr_docbook import router as ocr_docbook_router
from routes.docxmlindex import router as docxmlindex_router

# 6. Include Routers in a clean order
app.include_router(pdf_to_word.router)
app.include_router(pdf_to_tiff.router)
app.include_router(pdf_split.router)
app.include_router(ocr_preview.router)
app.include_router(ln_xml_router)
app.include_router(xml_job_router)
app.include_router(folder_router)
app.include_router(ln_xml_manual.router)
app.include_router(image_crop.router)
app.include_router(ocr_router)
app.include_router(ws_router)
app.include_router(pdf_to_xml.router)
app.include_router(bits_router)
app.include_router(split_pdf_router)
app.include_router(bits_meta_router)
app.include_router(xml_ref_router, prefix="/api/xml-ref")
app.include_router(case_reference_router)
app.include_router(build_router)
app.include_router(ocr_docbook_router)
app.include_router(docxmlindex_router)

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Black Vave Backend is Running Successfully"}







