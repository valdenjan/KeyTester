import json
import os
import glob

LAYOUTS_DIR = "layouts"
CHECKS_DIR = "checks"

def ensure_dirs():
    for d in (LAYOUTS_DIR, CHECKS_DIR):
        if not os.path.exists(d):
            os.makedirs(d)

def get_available_layouts():
    ensure_dirs()
    files = glob.glob(os.path.join(LAYOUTS_DIR, "*.json"))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]

def load_layout(name):
    path = os.path.join(LAYOUTS_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_check(data):
    ensure_dirs()
    safe_date = data['date'].replace(':', '-').replace(' ', '_')
    filename = f"report_{safe_date}.json"
    filepath = os.path.join(CHECKS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return filename

def load_check(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def delete_check(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)

def update_check(filepath, updated_data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)