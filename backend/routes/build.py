from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
import os, time, threading

from services.builder import build_output

router = APIRouter()


@router.post("/build")
async def build(
    section: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(...)
):
    return await build_output(section, type, file)


@router.get("/download/{file_id}/{filename}")
def download(file_id: str, filename: str):
    path = f"outputs/{file_id}_{filename}"

    if not os.path.exists(path):
        return {"error": "File expired or not found"}

    response = FileResponse(path, filename=filename)

    # delete after download
    def cleanup():
        time.sleep(2)
        if os.path.exists(path):
            os.remove(path)

    threading.Thread(target=cleanup, daemon=True).start()
    return response
