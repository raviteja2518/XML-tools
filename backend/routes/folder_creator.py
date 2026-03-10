from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import zipfile
import uuid

router = APIRouter()

BASE_DIR = "storage/zips"
os.makedirs(BASE_DIR, exist_ok=True)


def build_structure(base_path: str, structure: str):
    """
    Reads tree-like structure text and creates folders/files
    """
    stack = [base_path]

    for line in structure.splitlines():
        line = line.strip()

        if not line:
            continue

        # remove tree symbols
        clean = (
            line.replace("├─", "")
            .replace("└─", "")
            .replace("│", "")
            .strip()
        )

        if clean.endswith("/"):
            # folder
            folder_path = os.path.join(stack[0], clean[:-1])
            os.makedirs(folder_path, exist_ok=True)
        else:
            # file
            file_path = os.path.join(stack[0], clean)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")  # empty file


@router.post("/Tools/folder_creation")
def generate_folder_zip(
    projectName: str = Body(...),
    structure: str = Body(...)
):
    if not projectName or not structure:
        raise HTTPException(status_code=400, detail="Invalid input")

    job_id = str(uuid.uuid4())
    work_dir = os.path.join(BASE_DIR, job_id)
    os.makedirs(work_dir, exist_ok=True)

    project_dir = os.path.join(work_dir, projectName)
    os.makedirs(project_dir, exist_ok=True)

    # Build folders/files
    build_structure(project_dir, structure)

    # Create ZIP
    zip_path = os.path.join(BASE_DIR, f"{job_id}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_dir):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(
                    full_path,
                    arcname=os.path.relpath(full_path, project_dir)
                )

    # cleanup temp folder
    shutil.rmtree(work_dir)

    return {
        "download_url": f"/Tools/download/{job_id}"
    }


@router.get("/Tools/download/{job_id}")
def download_zip(job_id: str):
    zip_path = os.path.join(BASE_DIR, f"{job_id}.zip")

    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP not found")

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="project_structure.zip"
    )
