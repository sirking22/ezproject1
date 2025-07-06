import os
import time
from datetime import datetime, timedelta

CLEAN_PATHS = [
    "backups",
    "tmp",
]
CLEAN_EXTS = [".bak", ".tmp", ".json"]
MAX_AGE_DAYS = 1

def is_old(file_path, max_age_days=1):
    file_time = os.path.getmtime(file_path)
    return (time.time() - file_time) > (max_age_days * 86400)

def cleanup():
    deleted = []
    for folder in CLEAN_PATHS:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if not os.path.isfile(fpath):
                continue
            if any(fname.endswith(ext) for ext in CLEAN_EXTS) and is_old(fpath, MAX_AGE_DAYS):
                try:
                    os.remove(fpath)
                    deleted.append(fpath)
                except Exception as e:
                    print(f"Ошибка удаления {fpath}: {e}")
    print(f"Удалено файлов: {len(deleted)}")
    for f in deleted:
        print(f" - {f}")

if __name__ == "__main__":
    cleanup() 