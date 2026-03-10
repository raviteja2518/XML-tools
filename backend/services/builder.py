import os, uuid, time, threading

from services.front import build_front
from services.chapter import build_chapter
from services.back import build_back
from services.meta import build_meta

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
TTL_SECONDS = 1800


def auto_delete_file(path, delay=TTL_SECONDS):
    def _delete():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=_delete, daemon=True).start()


async def build_output(section, type, file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    uid = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{uid}_{file.filename}")

    # save upload
    with open(input_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    # route
    if section == "front":
        content, fname = build_front(type, input_path)
    elif section == "chapter":
        content, fname = build_chapter(type, input_path)
    elif section == "back":
        content, fname = build_back(type, input_path)
    elif section == "meta":
        content, fname = build_meta(type, input_path)
    else:
        return {"error": "Invalid section"}

    # save output
    output_path = os.path.join(OUTPUT_DIR, f"{uid}_{fname}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # delete input
    if os.path.exists(input_path):
        os.remove(input_path)

    # auto delete output
    auto_delete_file(output_path)

    return {
        "id": uid,
        "filename": fname,
        "content": content
    }
