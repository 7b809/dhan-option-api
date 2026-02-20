Option Chain API

A Flask-based backend service that:

Downloads instrument data

Builds daily JSON option-chain files

Serves filtered option-chain data via REST API

Rebuilds data automatically once per day

Project Structure
project/
│
├── app.py
├── downloader.py
├── config.py
├── last_build.txt
│
├── utils/
│   └── file_manager.py
│
└── data/
How It Works
1️⃣ Daily Rebuild Logic

The system checks if data was built today.

If not built → runs download_and_build()

If already built today → skips rebuild

Stores last build date inside last_build.txt

Functions Responsible
needs_rebuild()
mark_built_today()
2️⃣ Home Route
Endpoint
GET /
Purpose

Health check route to confirm server is running.

Sample Response
{
  "status": "Server is running",
  "service": "Option Chain API",
  "date": "2026-02-21"
}
3️⃣ Option Chain Route
Endpoint
GET /option-chain
Required Query Parameters
Parameter	Description
segment	Market segment
exchange	Exchange name
symbol	Underlying symbol
expiry	Expiry date
Example Request
http://127.0.0.1:5000/option-chain?segment=FO&exchange=NSE&symbol=NIFTY&expiry=2026-02-26
Success Response (Sample)
{
  "symbol": "NIFTY",
  "expiry": "2026-02-26",
  "data": [
    {
      "strike": 22000,
      "call_oi": 152340,
      "put_oi": 130220
    },
    {
      "strike": 22100,
      "call_oi": 142100,
      "put_oi": 155980
    }
  ]
}
Error Responses
Missing Parameters
{
  "error": "Missing parameters"
}

HTTP Status Code: 400

File Not Found
{
  "error": "File not found"
}

HTTP Status Code: 404

Rebuild Flow
Client Request
      ↓
Check last_build.txt
      ↓
If not today's date:
      ↓
Run download_and_build()
      ↓
Save today's date
      ↓
Serve JSON file
How To Run
1️⃣ Install Dependencies
pip install flask
2️⃣ Run Application
python app.py
3️⃣ Open in Browser

Health Check:

http://127.0.0.1:5000/

Option Chain:

http://127.0.0.1:5000/option-chain?segment=FO&exchange=NSE&symbol=NIFTY&expiry=2026-02-26
Production Recommendation

Instead of:

app.run(debug=True)

Use:

gunicorn app:app

Or deploy via:

Docker

Nginx + Gunicorn

Cloud VM (AWS / DigitalOcean / GCP)

Future Improvements

Add logging

Add rebuild time tracking

Add API key authentication

Add caching (Redis)

Add expiry listing endpoint

Add instruments listing endpoint

Add auto-scheduled rebuild (cron at 9:00 AM)

Summary

This API:

Builds option-chain files once per day

Serves JSON via REST

Automatically manages rebuild logic

Returns structured error handling

Designed for scalable trading backend systems