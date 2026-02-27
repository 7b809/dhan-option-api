import os
import json
from config import BASE_FOLDER

# ✅ External → Internal Segment Mapping
SEGMENT_MAP = {
    "FNO": "D",
    "DERIVATIVE": "D",
    "D": "D",
    "INDEX": "I",
    "I": "I"
}


def get_option_file(segment, exch, symbol, expiry):
    """
    Fetch option chain JSON file based on segment, exchange, symbol and expiry.
    External segment names are mapped to internal folder names.
    """

    # Normalize inputs
    segment = segment.upper().strip()
    exch = exch.upper().strip()
    symbol = symbol.upper().strip()
    expiry = expiry.strip()

    # Map external segment to folder segment
    segment_folder = SEGMENT_MAP.get(segment)

    if not segment_folder:
        print(f"[ERROR] Invalid segment received: {segment}")
        return None

    # Build full file path
    path = os.path.join(
        BASE_FOLDER,
        f"segment_{segment_folder}",
        exch,
        symbol,
        f"{expiry}.json"
    )

    print(f"[DEBUG] Looking for file at: {path}")

    if not os.path.exists(path):
        print("[ERROR] File does not exist.")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON: {e}")
        return None