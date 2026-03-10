import os, json
from datetime import datetime, timedelta

JOB_DIR = "storage/jobs"

def cleanup_expired_jobs():
    now = datetime.utcnow()

    if not os.path.exists(JOB_DIR):
        return

    for job_file in os.listdir(JOB_DIR):
        path = f"{JOB_DIR}/{job_file}"

        try:
            with open(path) as f:
                job = json.load(f)

            created = datetime.fromisoformat(job["created_at"])

            if now - created > timedelta(minutes=30):
                for p in [job["input_file"], job["output_file"], path]:
                    if os.path.exists(p):
                        os.remove(p)

        except Exception:
            continue
