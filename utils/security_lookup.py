import os
import json
from config import BASE_FOLDER

SECURITY_INDEX_FILE = os.path.join(BASE_FOLDER, "security_index.json")

_security_cache = None


def load_security_index():
    global _security_cache

    if _security_cache is None:
        if not os.path.exists(SECURITY_INDEX_FILE):
            return None

        with open(SECURITY_INDEX_FILE) as f:
            _security_cache = json.load(f)

    return _security_cache


def get_security_by_id(security_id: str):
    data = load_security_index()
    if not data:
        return None

    return data.get(security_id)