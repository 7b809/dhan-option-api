🚀 DHAN Option API Documentation

Base URL (Local):

http://127.0.0.1:5000
1️⃣ Health Check Route
🔹 Endpoint
GET /
🔹 Purpose

Checks if server is running.

🔹 Sample URL
http://127.0.0.1:5000/
🔹 Sample Response
{
  "status": "Server is running",
  "service": "Option Chain API",
  "date": "2026-02-22"
}
2️⃣ Option Chain Route
🔹 Endpoint
GET /option-chain
🔹 Required Query Parameters
Parameter	Example	Description
segment	D	Segment type
exchange	NSE	Exchange ID
symbol	NIFTY	Underlying symbol
expiry	2026-02-24	Expiry date (YYYY-MM-DD)
🔹 Sample URL
http://127.0.0.1:5000/option-chain?segment=D&exchange=NSE&symbol=NIFTY&expiry=2026-02-24
🔹 Sample Response
{
  "25500.00000": [
    {
      "SYMBOL_NAME": "NIFTY-Feb2026-25500-CE",
      "DISPLAY_NAME": "NIFTY 24 FEB 25500 CALL",
      "SECURITY_ID": "64854",
      "ISIN": "NA",
      "INSTRUMENT": "OPTIDX",
      "UNDERLYING_SECURITY_ID": "26000"
    },
    {
      "SYMBOL_NAME": "NIFTY-Feb2026-25500-PE",
      "DISPLAY_NAME": "NIFTY 24 FEB 25500 PUT",
      "SECURITY_ID": "64853",
      "ISIN": "NA",
      "INSTRUMENT": "OPTIDX",
      "UNDERLYING_SECURITY_ID": "26000"
    }
  ]
}
3️⃣ Security Lookup by Security ID
🔹 Endpoint
GET /security
🔹 Required Query Parameter
Parameter	Example
security_id	64872
🔹 Sample URL
http://127.0.0.1:5000/security?security_id=64872
🔹 Sample Response
{
  "EXCH_ID": "NSE",
  "SEGMENT": "D",
  "SECURITY_ID": "64872",
  "SYMBOL_NAME": "NIFTY-Feb2026-25600-CE",
  "DISPLAY_NAME": "NIFTY 24 FEB 25600 CALL",
  "STRIKE_PRICE": "25600.00000",
  "OPTION_TYPE": "CE",
  "SM_EXPIRY_DATE": "2026-02-24",
  ...
}

If not found:

{
  "error": "Security ID not found"
}
4️⃣ Contract Lookup (Smart Search)
🔹 Endpoint
GET /contract-lookup
🔹 Required Query Parameters
Parameter	Example	Description
symbol	NIFTY	Underlying
expiry	24FEB2026	Expiry (Flexible format)
strike	25500	Strike Price
type	CALL	CALL / PUT
🔹 Supported Expiry Formats

✔ 24FEB2026
✔ 24 FEB 2026

Backend automatically converts to:

2026-02-24
🔹 Sample URL
http://127.0.0.1:5000/contract-lookup?symbol=NIFTY&expiry=24FEB2026&strike=25500&type=CALL
🔹 Sample Response
{
  "EXCH_ID": "NSE",
  "SEGMENT": "D",
  "SECURITY_ID": "64854",
  "SYMBOL_NAME": "NIFTY-Feb2026-25500-CE",
  "DISPLAY_NAME": "NIFTY 24 FEB 25500 CALL",
  "STRIKE_PRICE": "25500.00000",
  "OPTION_TYPE": "CE",
  "SM_EXPIRY_DATE": "2026-02-24",
  ...
}

If not found:

{
  "error": "No matching contract found"
}
🔥 Automatic Rebuild Logic

Your API automatically:

Checks last_build.txt

If today’s data not built → runs download_and_build()

Ensures fresh master file daily

Builds:

security_index.json

option chain folders

This happens automatically on any route call.

🧠 Summary of All Routes
| Route              | Purpose                    |
| ------------------ | -------------------------- |
| `/`                | Health check               |
| `/option-chain`    | Get full option chain      |
| `/security`        | Lookup by Security ID      |
| `/contract-lookup` | Lookup by contract details |
