from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from PIL import Image
import uuid, os, time, threading

router = APIRouter()

BASE_DIR = "storage/image_crop"
PREVIEW_DIR = os.path.join(BASE_DIR, "preview")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

TTL_SECONDS = 30 * 60  # 30 minutes


# ===============================
# 🔥 FILE CLEANUP HELPERS
# ===============================
def safe_delete(*paths):
    time.sleep(2)
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Cleanup error: {e}")


def ttl_cleanup_worker():
    while True:
        now = time.time()

        for folder in [PREVIEW_DIR, OUTPUT_DIR]:
            for file in os.listdir(folder):
                path = os.path.join(folder, file)
                try:
                    if os.path.isfile(path):
                        if now - os.path.getctime(path) > TTL_SECONDS:
                            os.remove(path)
                except Exception:
                    pass

        time.sleep(300)  # every 5 mins


# 🔁 Start TTL cleaner once
threading.Thread(target=ttl_cleanup_worker, daemon=True).start()


# ===============================
# PREVIEW UPLOAD
# ===============================
@router.post("/tools/image-crop/preview")
async def upload_preview(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".tif", ".tiff")):
        raise HTTPException(status_code=400, detail="Only TIFF allowed")

    job_id = str(uuid.uuid4())

    tiff_path = os.path.join(PREVIEW_DIR, f"{job_id}.tiff")
    png_path = os.path.join(PREVIEW_DIR, f"{job_id}.png")

    with open(tiff_path, "wb") as f:
        f.write(await file.read())

    img = Image.open(tiff_path)
    img_rgb = img.convert("RGB")
    img_rgb.save(png_path, "PNG")

    return {
        "job_id": job_id,
        "preview_url": f"/tools/image-crop/preview/{job_id}",
        "width": img.width,
        "height": img.height,
    }


# ===============================
# PREVIEW VIEW
# ===============================
@router.get("/tools/image-crop/preview/{job_id}")
def get_preview(job_id: str):
    path = os.path.join(PREVIEW_DIR, f"{job_id}.png")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Preview expired")
    return FileResponse(path, media_type="image/png")


# ===============================
# IMAGE CROP
# ===============================
@router.post("/tools/image-crop")
async def image_crop(
    job_id: str = Form(...),
    x: int = Form(...),
    y: int = Form(...),
    width: int = Form(...),
    height: int = Form(...),
):
    tiff_path = os.path.join(PREVIEW_DIR, f"{job_id}.tiff")
    output_path = os.path.join(OUTPUT_DIR, f"{job_id}_300dpi.tiff")

    if not os.path.exists(tiff_path):
        raise HTTPException(status_code=404, detail="Preview expired")

    img = Image.open(tiff_path)

    x = max(0, x)
    y = max(0, y)
    width = min(width, img.width - x)
    height = min(height, img.height - y)

    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail="Invalid crop area")

    cropped = img.crop((x, y, x + width, y + height))
    cropped.save(output_path, dpi=(300, 300))

    return {
        "download_url": f"/tools/image-crop/download/{job_id}"
    }


# ===============================
# DOWNLOAD + AUTO DELETE
# ===============================
@router.get("/tools/image-crop/download/{job_id}")
def download_cropped(job_id: str, background_tasks: BackgroundTasks):
    preview_tiff = os.path.join(PREVIEW_DIR, f"{job_id}.tiff")
    preview_png = os.path.join(PREVIEW_DIR, f"{job_id}.png")
    output_tiff = os.path.join(OUTPUT_DIR, f"{job_id}_300dpi.tiff")

    if not os.path.exists(output_tiff):
        raise HTTPException(status_code=404, detail="File expired")

    # 🔥 delete EVERYTHING after download
    background_tasks.add_task(
        safe_delete,
        preview_tiff,
        preview_png,
        output_tiff
    )

    return FileResponse(
        output_tiff,
        media_type="image/tiff",
        filename="cropped_300dpi.tiff"
    )
