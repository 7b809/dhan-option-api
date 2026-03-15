import os

# Vercel writable directory
BASE_FOLDER = os.path.join("/tmp", "data")

ALLOWED_STRUCTURE = {
    "NSE": [
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "NIFTYNXT50"
    ],
    "BSE": [
        "SENSEX",
        "BANKEX"
    ]
}

DHAN_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"