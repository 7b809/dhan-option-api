from flask import Flask, request, jsonify
from downloader import download_and_build
from utils.file_manager import get_option_file
import os
import datetime
from config import BASE_FOLDER

app = Flask(__name__)

LAST_BUILD_FILE = "last_build.txt"


def needs_rebuild():
    if not os.path.exists(LAST_BUILD_FILE):
        return True

    with open(LAST_BUILD_FILE) as f:
        last_date = f.read().strip()

    today = datetime.date.today().isoformat()
    return last_date != today


def mark_built_today():
    today = datetime.date.today().isoformat()
    with open(LAST_BUILD_FILE, "w") as f:
        f.write(today)


@app.route("/option-chain", methods=["GET"])
def get_option_chain():
    segment = request.args.get("segment")
    exch = request.args.get("exchange")
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")

    if not all([segment, exch, symbol, expiry]):
        return jsonify({"error": "Missing parameters"}), 400

    # 🔥 Rebuild once per day
    if needs_rebuild():
        download_and_build()
        mark_built_today()

    data = get_option_file(segment, exch, symbol, expiry)

    if not data:
        return jsonify({"error": "File not found"}), 404

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)