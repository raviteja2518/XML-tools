import os, time

def delete_file(path: str):
    if os.path.exists(path):
        os.remove(path)

def schedule_delete(path: str, seconds: int):
    time.sleep(seconds)
    delete_file(path)
