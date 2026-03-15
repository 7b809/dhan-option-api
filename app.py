from flask import Flask, request, jsonify
from downloader import download_and_build
from utils.file_manager import get_option_file
from utils.security_lookup import get_security_by_id
from utils.security_lookup import find_security_by_contract
from flasgger import Swagger
import os
import datetime
from config import BASE_FOLDER
from flask import render_template


app = Flask(__name__)
Swagger(app)


LAST_BUILD_FILE = "/tmp/last_build.txt"

def needs_rebuild():
    if not os.path.exists(LAST_BUILD_FILE):
        return True

    with open(LAST_BUILD_FILE) as f:
        last_date = f.read().strip()
        f.close()

    today = datetime.date.today().isoformat()
    return last_date != today


def mark_built_today():
    today = datetime.date.today().isoformat()
    with open(LAST_BUILD_FILE, "w") as f:
        f.write(today)
        f.close()


@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

# ✅ Home Route (Server Health Check)
@app.route("/", methods=["GET"])
def home():
    """
    Server Health Check
    ---
    responses:
      200:
        description: Server running status
    """
    return jsonify({
        "status": "Server is running",
        "service": "Option Chain API",
        "sample":"/option-chain?segment=FNO&exchange=NSE&symbol=NIFTY&expiry=2026-03-17",
        "date": datetime.date.today().isoformat()
    })


@app.route("/option-chain", methods=["GET"])
def get_option_chain():
    """
    Get Option Chain
    ---
    parameters:
      - name: segment
        in: query
        type: string
        required: true
        example: FNO
      - name: exchange
        in: query
        type: string
        required: true
        example: NSE
      - name: symbol
        in: query
        type: string
        required: true
        example: NIFTY
      - name: expiry
        in: query
        type: string
        required: true
        example: 2026-03-17
    responses:
      200:
        description: Option chain data
      400:
        description: Missing parameters
      404:
        description: File not found
    """

    segment = request.args.get("segment")
    exch = request.args.get("exchange")
    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")

    if not all([segment, exch, symbol, expiry]):
        return jsonify({"error": "Missing parameters"}), 400

    if needs_rebuild():
        download_and_build()
        mark_built_today()

    data = get_option_file(segment, exch, symbol, expiry)

    if not data:
        return jsonify({"error": "File not found"}), 404

    return jsonify(data)


@app.route("/security", methods=["GET"])
def get_security():
    """
    Get Security by Security ID
    ---
    parameters:
      - name: security_id
        in: query
        type: string
        required: true
        example: 38737
    responses:
      200:
        description: Security details
      400:
        description: security_id missing
      404:
        description: Security ID not found
    """

    security_id = request.args.get("security_id")

    if not security_id:
        return jsonify({"error": "security_id is required"}), 400

    if needs_rebuild():
        download_and_build()
        mark_built_today()

    data = get_security_by_id(security_id)

    if not data:
        return jsonify({"error": "Security ID not found"}), 404

    return jsonify(data)


@app.route("/contract-lookup", methods=["GET"])
def contract_lookup():
    """
    Find Contract by Details
    ---
    parameters:
      - name: symbol
        in: query
        type: string
        required: true
        example: NIFTY
      - name: expiry
        in: query
        type: string
        required: true
        example: 25 JUN 2030
      - name: strike
        in: query
        type: string
        required: true
        example: 49500
      - name: type
        in: query
        type: string
        required: true
        example: CALL
    responses:
      200:
        description: Matching contract
      400:
        description: Missing parameters
      404:
        description: No matching contract found
    """

    symbol = request.args.get("symbol")
    expiry = request.args.get("expiry")
    strike = request.args.get("strike")
    option_type = request.args.get("type")

    if not all([symbol, expiry, strike, option_type]):
        return jsonify({"error": "Missing parameters"}), 400

    if needs_rebuild():
        download_and_build()
        mark_built_today()

    result = find_security_by_contract(symbol, expiry, strike, option_type)

    if not result:
        return jsonify({"error": "No matching contract found"}), 404

    return jsonify(result)


# =============================
# NEW ROUTE: LIST SYMBOLS
# =============================
@app.route("/symbols", methods=["GET"])
def get_symbols():
    """
    List Available Symbols
    ---
    parameters:
      - name: segment
        in: query
        type: string
        required: true
        example: FNO
      - name: exchange
        in: query
        type: string
        required: true
        example: NSE
    responses:
      200:
        description: List of available symbols
    """

    segment = request.args.get("segment")
    exchange = request.args.get("exchange")

    if not all([segment, exchange]):
        return jsonify({"error": "Missing parameters"}), 400

    segment_map = {
        "FNO": "segment_D",
        "INDEX": "segment_I"
    }

    segment_folder = segment_map.get(segment.upper())

    if not segment_folder:
        return jsonify({"error": "Invalid segment"}), 400

    path = os.path.join(BASE_FOLDER, segment_folder, exchange)

    if not os.path.exists(path):
        return jsonify({"symbols": []})

    symbols = [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name))
    ]

    return jsonify({"symbols": symbols})


# =============================
# NEW ROUTE: LIST EXPIRIES
# =============================
@app.route("/expiries", methods=["GET"])
def get_expiries():
    """
    List Expiries for Symbol
    ---
    parameters:
      - name: segment
        in: query
        type: string
        required: true
        example: FNO
      - name: exchange
        in: query
        type: string
        required: true
        example: NSE
      - name: symbol
        in: query
        type: string
        required: true
        example: NIFTY
    responses:
      200:
        description: List of expiries
    """

    segment = request.args.get("segment")
    exchange = request.args.get("exchange")
    symbol = request.args.get("symbol")

    if not all([segment, exchange, symbol]):
        return jsonify({"error": "Missing parameters"}), 400

    segment_map = {
        "FNO": "segment_D",
        "INDEX": "segment_I"
    }

    segment_folder = segment_map.get(segment.upper())

    path = os.path.join(BASE_FOLDER, segment_folder, exchange, symbol)

    if not os.path.exists(path):
        return jsonify({"expiries": []})

    expiries = [
        f.replace(".json", "")
        for f in os.listdir(path)
        if f.endswith(".json")
    ]

    return jsonify({"expiries": sorted(expiries)})


@app.route("/routes", methods=["GET"])
def list_all_routes():
    """
    List all possible API routes
    ---
    responses:
      200:
        description: All possible API routes
    """

    routes = {
        "option_chain_routes": [],
        "index_routes": [],
        "symbol_routes": [],
        "expiry_routes": []
    }

    # FNO routes
    fno_path = os.path.join(BASE_FOLDER, "segment_D")

    if os.path.exists(fno_path):
        for exch in os.listdir(fno_path):
            exch_path = os.path.join(fno_path, exch)

            routes["symbol_routes"].append(
                f"/symbols?segment=FNO&exchange={exch}"
            )

            for symbol in os.listdir(exch_path):
                symbol_path = os.path.join(exch_path, symbol)

                routes["expiry_routes"].append(
                    f"/expiries?segment=FNO&exchange={exch}&symbol={symbol}"
                )

                for file in os.listdir(symbol_path):
                    expiry = file.replace(".json", "")

                    routes["option_chain_routes"].append(
                        f"/option-chain?segment=FNO&exchange={exch}&symbol={symbol}&expiry={expiry}"
                    )

    # INDEX routes
    idx_path = os.path.join(BASE_FOLDER, "segment_I")

    if os.path.exists(idx_path):
        for exch in os.listdir(idx_path):

            routes["symbol_routes"].append(
                f"/symbols?segment=INDEX&exchange={exch}"
            )

            exch_path = os.path.join(idx_path, exch)

            for symbol in os.listdir(exch_path):

                routes["expiry_routes"].append(
                    f"/expiries?segment=INDEX&exchange={exch}&symbol={symbol}"
                )

                symbol_path = os.path.join(exch_path, symbol)

                for file in os.listdir(symbol_path):
                    expiry = file.replace(".json", "")

                    routes["index_routes"].append(
                        f"/option-chain?segment=INDEX&exchange={exch}&symbol={symbol}&expiry={expiry}"
                    )

    return jsonify(routes)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)