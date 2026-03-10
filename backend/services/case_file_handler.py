import os, uuid

BASE_DIR = "temp"
UPLOAD_DIR = f"{BASE_DIR}/uploads"
OUTPUT_DIR = f"{BASE_DIR}/outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_upload(file_bytes: bytes, ext: str):
    job_id = str(uuid.uuid4())
    path = f"{UPLOAD_DIR}/{job_id}.{ext}"
    with open(path, "wb") as f:
        f.write(file_bytes)
    return job_id, path

def output_path(job_id: str):
    return f"{OUTPUT_DIR}/{job_id}.xml"
