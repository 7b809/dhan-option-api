from flask import Flask, request, jsonify
from downloader import download_and_build
from utils.file_manager import get_option_file
from utils.security_lookup import get_security_by_id
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


# ✅ Home Route (Server Health Check)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "Server is running",
        "service": "Option Chain API",
        "date": datetime.date.today().isoformat()
    })


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

@app.route("/security", methods=["GET"])
def get_security():
    security_id = request.args.get("security_id")

    if not security_id:
        return jsonify({"error": "security_id is required"}), 400

    # 🔥 Rebuild once per day
    if needs_rebuild():
        download_and_build()
        mark_built_today()

    data = get_security_by_id(security_id)

    if not data:
        return jsonify({"error": "Security ID not found"}), 404

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)