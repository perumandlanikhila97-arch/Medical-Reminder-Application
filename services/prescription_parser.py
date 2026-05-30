import csv
import os

from utils.validators import parse_times_field


def parse_prescription_file(path):
    extension = os.path.splitext(path)[1].lower()
    medicines = []

    if extension == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                dose = row.get("dose", "").strip()
                times_raw = row.get("times", "").strip()
                notes = row.get("notes", "").strip()
                if not name or not times_raw:
                    continue
                times = parse_times_field(times_raw)
                if not times:
                    continue
                medicines.append({
                    "name": name,
                    "dose": dose,
                    "times": times,
                    "notes": notes,
                })
    elif extension == ".txt":
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = [part.strip() for part in line.strip().split(",")]
                if len(parts) < 3:
                    continue
                name = parts[0]
                dose = parts[1]
                times_raw = parts[2]
                notes = ", ".join(parts[3:]) if len(parts) > 3 else ""
                times = parse_times_field(times_raw)
                if not name or not times:
                    continue
                medicines.append({
                    "name": name,
                    "dose": dose,
                    "times": times,
                    "notes": notes,
                })
    else:
        raise ValueError("Unsupported prescription file type. Please use CSV or TXT.")

    return medicines
