# LuxeStay — Bali Retreat

## Hotel Reservation and Management System

LuxeStay is a modern, cloud-based hotel reservation and management system designed to simplify room management, guest registration, reservation tracking, check-in and check-out operations, and payment status monitoring. It features a tropical Bali Retreat-inspired interface integrated with Firebase Cloud Firestore for persistent database storage.

## Live Website

**Vercel Deployment:** https://luxestay-chariz1.vercel.app/

## Technologies Used

- Python Flask
- HTML5
- CSS3
- JavaScript
- Firebase Cloud Firestore
- Firebase Admin SDK
- Python-dotenv
- PyCharm
- GitHub
- Vercel

## System Features

- Interactive hotel management dashboard
- Room management
- Guest information management
- Reservation management
- Check-in and check-out management
- Payment status monitoring
- Create, Read, Update, and Delete (CRUD) operations
- Search and filtering
- Individual record viewing
- Automatic reservation cost calculation
- Double-booking prevention
- Input validation
- Cloud database integration
- Responsive Bali Retreat-inspired interface

## Database Collections

The system uses three interconnected Firebase Cloud Firestore collections.

| Collection | Description |
|---|---|
| `rooms` | Stores hotel room information, capacity, rates, amenities, and operational status. |
| `guests` | Stores guest information and contact details. |
| `reservations` | Stores booking details, room and guest references, reservation dates, costs, and payment status. |

The system also uses `_system/write_guard` as an internal transaction serialization document to help prevent conflicting reservations.

Rooms and guests are referenced by their Firestore document IDs. Collections are automatically created upon the first successful data insertion.

## Project Structure

- `app.py` — Flask application and REST API
- `firebase_config.py` — Firebase connection configuration
- `templates/index.html` — Main website interface
- `static/css/style.css` — Website styling and layout
- `static/js/app.js` — Frontend functionality and API integration
- `requirements.txt` — Python dependencies
- `.env.example` — Environment configuration template
- `.gitignore` — Excluded files and credentials
- `README.md` — Project documentation

## Local Installation and Setup

### 1. Firebase Configuration

Create a Firebase project and enable Cloud Firestore in production mode.

Navigate to Project Settings → Service Accounts → Generate New Private Key.

Save the downloaded file locally as `ServiceAccountKey.json`.

### 2. Environment Configuration

Create a `.env` file containing:

`GOOGLE_APPLICATION_CREDENTIALS=ServiceAccountKey.json`

`FLASK_DEBUG=false`

### 3. Install Dependencies

Open the project in PyCharm and run the following commands in Windows PowerShell:

`py -m venv .venv`

`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

### 4. Run the Application

`.\.venv\Scripts\python.exe app.py`

Open the local website:

http://127.0.0.1:5000/

### 5. Verify Firestore Connection

http://127.0.0.1:5000/api/health

## Vercel Deployment

The application is deployed using Vercel for online accessibility.

**Deployment URL:** https://luxestay-chariz1.vercel.app/

Firebase authentication is configured through the Vercel environment variable `FIREBASE_SERVICE_ACCOUNT`, which contains the Firebase service account JSON credentials.

The application supports both local Firebase credential files and Vercel environment variables.

To check the deployed database connection, visit:

https://luxestay-chariz1.vercel.app/api/health

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check database connectivity |
| GET | `/api/rooms` | Retrieve room records |
| GET | `/api/guests` | Retrieve guest records |
| GET | `/api/reservations` | Retrieve reservation records |
| POST | `/api/<collection>` | Create a record |
| GET | `/api/<collection>/<id>` | View a specific record |
| PUT | `/api/<collection>/<id>` | Update a record |
| DELETE | `/api/<collection>/<id>` | Delete a record |

List endpoints support search and status filtering.

## Business Rules and Validation

- Reservations require valid room and guest references.
- Overlapping active reservations are prevented.
- Check-out dates must be later than check-in dates.
- Pending, Confirmed, and Checked-in reservations block overlapping bookings.
- Room capacity and reservation details are validated.
- Existing reservation rates are preserved unless the assigned room changes.
- Linked rooms and guests cannot be deleted while referenced by reservations.
- Payment records represent payment status only and do not process actual financial transactions.

## Security and Privacy

Firebase credentials are securely managed through local environment files or Vercel Environment Variables.

The following files must never be uploaded to GitHub:

- `ServiceAccountKey.json`
- `.env`
- `.venv/`
- `__pycache__/`
- `.idea/`

Firestore security rules should deny direct client access. Database operations are performed through the Flask backend using the Firebase Admin SDK.

This application is intended for academic demonstration purposes. The deployed version does not include complete user authentication and authorization. Use fictional guest records only. Production use requires additional security measures.

## System Testing

The following operations should be verified:

- Firebase database connectivity
- Creating, viewing, updating, and deleting records
- Room and guest references
- Reservation cost calculations
- Double-booking prevention
- Search and filtering
- Input validation
- Linked-record deletion restrictions
- Data persistence after refreshing the website
- Local and Vercel application functionality

## Project Limitations

- Requires an internet connection for Firebase Cloud Firestore.
- External hotel images require internet access.
- Does not support actual online payment processing.
- Does not include complete production-level authentication.
- No automatic seed data is inserted by default.

## Academic Purpose

This project was developed as a final practical activity for the Advanced Database subject to demonstrate cloud database integration, interconnected collections, REST API development, CRUD operations, data validation, and web application deployment.

## Submission Requirements

- Private GitHub repository
- Complete project source code
- Firebase Cloud Firestore integration
- README documentation
- Vercel website deployment
- GitHub collaborator: `kidlat14`
- Submission before December 7, 2026
- December 6, 2026 or earlier for full timeliness points

---

**LuxeStay — Bali Retreat**

*Experience tropical elegance through smarter hotel management.*

Powered by Python Flask, Firebase Cloud Firestore, and Vercel.

© 2026 LuxeStay. Developed for educational purposes.
