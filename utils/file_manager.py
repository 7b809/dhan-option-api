import os
import json
from config import BASE_FOLDER


def get_option_file(segment, exch, symbol, expiry):
    path = os.path.join(
        BASE_FOLDER,
        f"segment_{segment}",
        exch,
        symbol,
        f"{expiry}.json"
    )

    if not os.path.exists(path):
        return None

    with open(path) as f:
        return json.load(f)