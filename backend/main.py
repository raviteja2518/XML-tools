import sys
import os
import time
import asyncio
import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models
from database import engine, SessionLocal
from auth import get_password_hash
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# ================= BACKGROUND CLEANUP =================
async def cleanup_old_files():
    """Scans and deletes files older than 30 minutes in target directories."""
    target_dirs = ["outputs", "temp_jobs"]
    max_age_seconds = 30 * 60  # 30 minutes
    
    while True:
        try:
            now = time.time()
            for directory in target_dirs:
                if not os.path.exists(directory):
                    continue
                    
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    # Skip if it's not a file/dir or we can't get modified time
                    try:
                        mtime = os.path.getmtime(file_path)
                        if now - mtime > max_age_seconds:
                            if os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                            else:
                                os.remove(file_path)
                            print(f"🧹 Auto-deleted expired file: {file_path}")
                    except Exception as e:
                        print(f"Error checking/deleting file {file_path}: {e}")
        except Exception as e:
            print(f"Cleanup task encountered an error: {e}")
            
        await asyncio.sleep(300)  # Wait 5 minutes before next sweep

# ================= DB INIT =================
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background cleanup task
    cleanup_task = asyncio.create_task(cleanup_old_files())
    
    # Seed admin user on startup
    db = SessionLocal()
    try:
        admin_email = "admin@vavetech.com"
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_user:
            new_admin = models.User(
                name="System Admin",
                email=admin_email,
                phone="0000000000",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()
    
    yield
    
    # Cancel the background task on shutdown
    cleanup_task.cancel()

# ================= FASTAPI INIT =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


app = FastAPI(title="Black Vave Multi-Tool API", lifespan=lifespan)

# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "*") 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STATIC DIRECTORIES =================

os.makedirs("outputs", exist_ok=True)
os.makedirs("temp_jobs", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/temp_jobs", StaticFiles(directory="temp_jobs"), name="temp_jobs")
os.makedirs("uploads/profile_pictures", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ================= IMPORT ROUTERS =================

from routes import (
    pdf_to_tiff,
    pdf_split,
    ocr_preview,
    ln_xml_manual,
    image_crop,
    pdf_to_xml,
    split_pdf
)

from routes.ln_xml import router as ln_xml_router
from routes.xml_job import router as xml_job_router
from routes.folder_creator import router as folder_router
from routes.ws_progress import router as ws_router
from routes.bits_pdf_to_xml import router as bits_router
from routes.bits_meta import router as bits_meta_router
from routes.xml_ref import xml_ref_router
from routes.case_reference import case_reference_router
from routes.build import router as build_router
from routes.ocr_docbook import router as ocr_docbook_router
from routes.docxmlindex import router as docxmlindex_router
from routes.tail_ref import router as tail_router
from routes.pdf_to_word import router as pdf_word_router

from routes.auth_routes import router as auth_router
from routes.admin_routes import router as admin_router
from routes.payment_routes import router as payment_router
from routes.profile_routes import router as profile_router
from dependencies import get_current_active_user
from fastapi import Depends

# ================= INCLUDE ROUTERS =================

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(payment_router)
app.include_router(profile_router)

# Protect existing tools using dependencies
tool_deps = [Depends(get_current_active_user)]

app.include_router(pdf_to_tiff.router, prefix="/api", dependencies=tool_deps)
app.include_router(pdf_split.router, prefix="/api", dependencies=tool_deps)
app.include_router(ocr_preview.router, prefix="/api", dependencies=tool_deps)

app.include_router(ln_xml_router)
app.include_router(xml_job_router)
app.include_router(folder_router)

app.include_router(ln_xml_manual.router, prefix="/api")
app.include_router(image_crop.router, prefix="/api")
app.include_router(ws_router, prefix="/api")

app.include_router(pdf_to_xml.router, prefix="/api", dependencies=tool_deps)
app.include_router(bits_router, prefix="/api", dependencies=tool_deps)
app.include_router(split_pdf.router, prefix="/api", dependencies=tool_deps)
app.include_router(bits_meta_router, prefix="/api", dependencies=tool_deps)

app.include_router(xml_ref_router, prefix="/api/xml-ref", dependencies=tool_deps)

app.include_router(case_reference_router, prefix="/api", dependencies=tool_deps)
app.include_router(build_router, prefix="/api", dependencies=tool_deps)

app.include_router(ocr_docbook_router, prefix="/api", dependencies=tool_deps)
app.include_router(docxmlindex_router, prefix="/api", dependencies=tool_deps)
app.include_router(pdf_word_router, prefix="/api", dependencies=tool_deps)
# Tail reference parser
app.include_router(tail_router, prefix="/api", dependencies=tool_deps)

# ================= ROOT HEALTH CHECK =================

@app.get("/")
async def root():
    return {"message": "Black Vave Backend is Running Successfully"}