from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pdf2docx import Converter
import uuid, os, threading, time, asyncio, json

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONVERT_DIR = os.path.join(BASE_DIR, "storage", "pdf_word")

os.makedirs(CONVERT_DIR, exist_ok=True)

TTL_SECONDS = 1800


progress_store = {}
job_status = {}
job_created_at = {}


def convert_worker(job_id: str, pdf_path: str):

    try:

        progress_store[job_id] = 10

        output_path = os.path.join(CONVERT_DIR, f"{job_id}.docx")

        cv = Converter(pdf_path)

        cv.convert(output_path)

        cv.close()

        progress_store[job_id] = 100

        job_status[job_id] = "completed"

        os.remove(pdf_path)

    except Exception as e:

        print("ERROR:", e)

        job_status[job_id] = "failed"


@router.post("/tools/pdf-to-word")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    job_id = str(uuid.uuid4())

    pdf_path = os.path.join(CONVERT_DIR, f"{job_id}.pdf")

    with open(pdf_path,"wb") as f:
        f.write(await file.read())

    progress_store[job_id] = 1
    job_status[job_id] = "processing"
    job_created_at[job_id] = time.time()

    threading.Thread(
        target=convert_worker,
        args=(job_id,pdf_path),
        daemon=True
    ).start()

    return {
        "job_id": job_id,
        "download_url": f"/tools/download/{job_id}"
    }


@router.get("/events/pdf-to-word-progress/{job_id}")
async def progress_events(job_id: str):

    async def event_generator():

        last = -1

        while True:

            progress = progress_store.get(job_id,0)

            if progress != last:

                yield f"data: {json.dumps({'progress':progress})}\n\n"

                last = progress

            if progress >= 100:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/tools/download/{job_id}")
def download(job_id:str, background_tasks: BackgroundTasks):

    file_path = os.path.join(CONVERT_DIR, f"{job_id}.docx")

    if not os.path.exists(file_path):
        raise HTTPException(404,"File not found")

    background_tasks.add_task(cleanup,job_id)

    return FileResponse(
        file_path,
        filename="converted.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def cleanup(job_id):

    time.sleep(2)

    files = [
        os.path.join(CONVERT_DIR,f"{job_id}.docx"),
        os.path.join(CONVERT_DIR,f"{job_id}.pdf")
    ]

    for f in files:
        if os.path.exists(f):
            os.remove(f)

    progress_store.pop(job_id,None)
    job_status.pop(job_id,None)
    job_created_at.pop(job_id,None)