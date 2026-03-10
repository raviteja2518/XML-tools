import time, os

def schedule_cleanup(path: str, ttl: int):
    time.sleep(ttl)
    if os.path.exists(path):
        os.remove(path)
