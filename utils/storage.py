import csv
import os
from datetime import datetime

LOG_FILE = "data/usage_log.csv"

FIELDNAMES = [
    "timestamp",
    "page",
    "event_type",
    "topic",
    "verse_reference",
    "difficulty",
    "is_correct",
    "used_fallback",
]

def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()

def log_event(
    page,
    event_type,
    topic="",
    verse_reference="",
    difficulty="",
    is_correct="",
    used_fallback="",
):
    ensure_log_file()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "page": page,
            "event_type": event_type,
            "topic": topic,
            "verse_reference": verse_reference,
            "difficulty": difficulty,
            "is_correct": is_correct,
            "used_fallback": used_fallback,
        })