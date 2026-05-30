from datetime import datetime

def parse_times_field(field):
    parts = []

    for sep in (";", ","):
        if sep in field:
            parts = [
                p.strip()
                for p in field.split(sep)
                if p.strip()
            ]
            break

    if not parts:
        parts = [field.strip()] if field.strip() else []

    valid = []
    for p in parts:
        try:
            datetime.strptime(p, "%H:%M")
            valid.append(p)
        except Exception:
            pass

    return valid
    