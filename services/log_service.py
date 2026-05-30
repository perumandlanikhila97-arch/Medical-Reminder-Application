import csv
import os
from datetime import datetime
from Config.settings import LOG_FILE

def ensure_log():
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["timestamp", "medicine", "dose", "note", "status"]
            )


def log_event(medicine, dose, note, status):
    ensure_log()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            medicine,
            dose,
            note,
            status
        ])