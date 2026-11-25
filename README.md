# LuxeStay — Bali Retreat
Flask REST API, HTML/CSS/JavaScript, Firebase Cloud Firestore. Python 3.11+ recommended.

## Setup (Windows PowerShell)
1. Create a Firebase project and enable Cloud Firestore in production mode.
2. Project settings > Service accounts > Generate new private key. Save it locally as `ServiceAccountKey.json`. Never commit it.
3. Copy `.env.example` to `.env` if missing. Set the credential path.
4. Run `py -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, then `.\.venv\Scripts\python.exe app.py`.
5. Open http://127.0.0.1:5000 and check http://127.0.0.1:5000/api/health.

## Database
Rooms and guests are referenced by document ID in reservations. The first successful insert creates each collection. `_system/write_guard` is an internal transaction serialization document. Do not edit data directly while using the app. All writes use Flask and the Admin SDK. Room status is operational; booked status is derived from active reservations for today's date. Pending, Confirmed and Checked-in reservations block overlapping dates; checkout is exclusive. Existing reservation rates are preserved unless the room changes. Payments are status records, not payment processing. Amenities are stored as text. Photos are illustrative external images and require internet access; fonts have fallbacks.

## Security
Use Firestore rules `rules_version = '2'; service cloud.firestore { match /databases/{database}/documents { match /{document=**} { allow read, write: if false; } } }` for direct client access. Admin SDK bypasses rules and uses IAM. This is a local single-operator classroom app, not an authenticated public hotel service. Do not expose it publicly or enter real guest personal data without adding authentication and authorization.

## API
GET/POST `/api/rooms`, `/api/guests`, `/api/reservations`; GET/PUT/DELETE `/api/<collection>/<id>`. List GET accepts `q` and `status`. UI also filters locally. `/api/health` checks Firestore.

## Manual verification
Create a room and guest, then a reservation. Verify totals, view, edit, search, and refresh. Attempt an overlapping reservation and confirm rejection. Attempt deleting a linked room and confirm rejection. Delete reservation, then room and guest. Verify documents in Firebase console. Test invalid dates, capacity and missing IDs. Check-in/out and payment pages use reservation editing. No seed data is inserted.

## Submission
Create a private GitHub repository, invite `kidlat14`, push source and README, excluding credentials and `.env`. Submit before December 7, 2026 (December 6 or earlier for full timeliness points).
