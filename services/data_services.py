import json
import os 
from Config.settings import DATA_FILE

def load_medicines():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_medicines(medicines):
    data_dir = os.path.dirname(DATA_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(medicines, f, indent=2)
        