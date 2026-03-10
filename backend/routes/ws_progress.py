from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json
import time

router = APIRouter()

# ===============================
# IN-MEMORY PROGRESS STORE
# ===============================
# key: job_id, value: progress (0–100)
progress_store = {}

# optional: track creation time (TTL use)
job_created_at = {}

TTL_SECONDS = 30 * 60  # 30 minutes


# ===============================
# SET PROGRESS (CALL FROM WORKER)
# ===============================
def set_progress(job_id: str, value: int):
    progress_store[job_id] = value
    job_created_at.setdefault(job_id, time.time())


# ===============================
# SSE PROGRESS ENDPOINT (BEST)
# ===============================
@router.get("/events/ocr-progress/{job_id}")
async def sse_progress(job_id: str):

    async def event_generator():
        last_sent = -1

        while True:
            progress = progress_store.get(job_id, 0)

            # send only if progress changed
            if progress != last_sent:
                yield f"data: {json.dumps({'job_id': job_id, 'progress': progress})}\n\n"
                last_sent = progress

            # stop stream when job completes
            if progress >= 100:
                break

            await asyncio.sleep(0.3)  # smooth real-time updates

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ===============================
# CLEANUP (CALL AFTER DOWNLOAD)
# ===============================
def cleanup_job(job_id: str):
    progress_store.pop(job_id, None)
    job_created_at.pop(job_id, None)


# ===============================
# TTL AUTO CLEANER (OPTIONAL)
# ===============================
async def ttl_cleanup_worker():
    while True:
        now = time.time()
        for job_id in list(job_created_at.keys()):
            if now - job_created_at[job_id] > TTL_SECONDS:
                cleanup_job(job_id)
        await asyncio.sleep(300)  # every 5 mins
