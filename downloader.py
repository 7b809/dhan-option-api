import requests
import csv
import os
import json
from collections import defaultdict
from config import BASE_FOLDER, ALLOWED_STRUCTURE, DHAN_URL


FIELDS_TO_KEEP = [
    "SYMBOL_NAME",
    "DISPLAY_NAME",
    "SECURITY_ID",
    "ISIN",
    "INSTRUMENT",
    "UNDERLYING_SECURITY_ID"
]

SECURITY_INDEX_FILE = os.path.join(BASE_FOLDER, "security_index.json")


def filter_fields(row):
    return {k: row.get(k) for k in FIELDS_TO_KEEP}


def download_and_build():
    print("[INFO] Downloading master file...")

    response = requests.get(DHAN_URL)
    response.raise_for_status()

    decoded = response.content.decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    grouped = defaultdict(list)

    # 🔥 Security ID index dictionary (FULL ROWS)
    security_index = {}

    for row in reader:
        segment = row.get("SEGMENT")
        exch = row.get("EXCH_ID")
        underlying = row.get("UNDERLYING_SYMBOL", "").upper()
        expiry = row.get("SM_EXPIRY_DATE")

        # 🔥 STORE FULL ROW (NOT filtered)
        security_id = row.get("SECURITY_ID")
        if security_id:
            security_index[security_id] = row  # ✅ full row saved

        # 🔥 Existing Logic (UNCHANGED)
        if exch in ALLOWED_STRUCTURE and underlying in ALLOWED_STRUCTURE[exch]:
            key = (segment, exch, underlying, expiry)
            grouped[key].append(row)

    # Delete old data folder (UNCHANGED)
    if os.path.exists(BASE_FOLDER):
        import shutil
        shutil.rmtree(BASE_FOLDER)

    # Recreate base folder
    os.makedirs(BASE_FOLDER, exist_ok=True)

    # 🔥 Save FULL security index
    with open(SECURITY_INDEX_FILE, "w") as f:
        json.dump(security_index, f, indent=4)

    # 🔥 Existing Option Chain Build Logic (UNCHANGED)
    for (segment, exch, underlying, expiry), rows in grouped.items():

        folder_path = os.path.join(
            BASE_FOLDER,
            f"segment_{segment}",
            exch,
            underlying
        )

        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, f"{expiry}.json")

        if segment == "D":
            strike_dict = defaultdict(lambda: [None, None])

            for row in rows:
                strike = row.get("STRIKE_PRICE")
                option_type = row.get("OPTION_TYPE", "").upper()

                minimal = filter_fields(row)

                if option_type == "CE":
                    strike_dict[strike][0] = minimal
                elif option_type == "PE":
                    strike_dict[strike][1] = minimal

            cleaned = {
                strike: data
                for strike, data in strike_dict.items()
                if data[0] or data[1]
            }

            with open(file_path, "w") as f:
                json.dump(cleaned, f)

    print("[INFO] Data build complete.")