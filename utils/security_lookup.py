import os
import json
from config import BASE_FOLDER
from datetime import datetime
import re

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



def parse_expiry(expiry_str: str):
    """
    Converts:
    24FEB2026  -> 2026-02-24
    24 FEB 2026 -> 2026-02-24
    """

    expiry_str = expiry_str.strip().upper()

    # Case 1: 24FEB2026
    match = re.match(r"(\d{2})([A-Z]{3})(\d{4})", expiry_str)
    if match:
        day, month, year = match.groups()
        date_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
        return date_obj.strftime("%Y-%m-%d")

    # Case 2: 24 FEB 2026
    try:
        date_obj = datetime.strptime(expiry_str, "%d %b %Y")
        return date_obj.strftime("%Y-%m-%d")
    except:
        return None


def find_security_by_contract(symbol, expiry, strike, option_type):
    data = load_security_index()
    if not data:
        return None

    expiry_date = parse_expiry(expiry)
    if not expiry_date:
        return None

    option_type = option_type.upper()
    option_type = "CE" if option_type in ["CALL", "CE"] else "PE"

    strike = str(float(strike))

    for sec_id, row in data.items():
        if (
            row.get("UNDERLYING_SYMBOL", "").upper() == symbol.upper()
            and row.get("SM_EXPIRY_DATE") == expiry_date
            and str(float(row.get("STRIKE_PRICE", 0))) == strike
            and row.get("OPTION_TYPE", "").upper() == option_type
        ):
            return row

    return None