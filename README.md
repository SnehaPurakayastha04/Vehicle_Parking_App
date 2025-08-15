# VehicleBay: Vehicle Parking Management System

A Flask-based web application to manage vehicle parking lots, bookings, and payments.  
This project is part of the **IITM BS Degree - MAD 1 Project**.

---

## Features
- **User Registration & Login** (with authentication)
- **Admin Dashboard** to:
  - Add/Edit/Delete Parking Lots
  - View occupied and available parking spots
  - View monthly revenue and reservations chart
- **User Dashboard** to:
  - View available parking lots
  - Book parking spots
  - Release parking spots & view payment summary
- **Charts & Analytics** using Chart.js
- **SQLite Database** for data storage

---

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate
- **Frontend:** HTML, CSS, Bootstrap, Jinja2 Templates, Chart.js
- **Database:** SQLite

---

## Project Structure
vehicle_bay/                   # Root project folder
│
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── PROJECT REPORT.pdf         # Project documentation
├── README.md                  # Project description for GitHub
├── .gitignore                 # Files/folders to ignore in GitHub
│
├── instance/                  # Stores the SQLite database file
│   └── vehicle_bay.db
│
├── migrations/                # Flask-Migrate files for database changes
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── static/                    # Static assets
│   └── css/
│       ├── bootstrap.min.css
│       └── style.css
│
├── Templates/                 # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── parking_lot_detail.html
│   ├── admin_summary_chart.html
│   └── ...
│
└── venv/                      # Python virtual environment

## How It Works
### User Registration & Login

A new user can register with their details.

Login form validates credentials and grants access to the user dashboard.

### Admin Access

Admin has a separate dashboard to:

Add/Edit/Delete parking lots

View all registered users

Monitor spot status (Available / Occupied)

View charts of monthly reservations & revenue using Chart.js

### Booking a Parking Spot

User selects a parking lot.

If they don’t already have an active booking, they can:

Choose an available spot.

Enter vehicle number.

Reservation is stored in the database with start time, spot ID, and user ID.

Spot status changes from "A" (Available) to "O" (Occupied).

### Viewing Parking Lot Details

Shows lot information (name, address, pincode, price/hr, total spots).

Lists each spot:

Spot ID

Status (Available/Occupied)

Vehicle Number (if occupied)

Username of user occupying

### Admin Summary Charts


Monthly reservations count

Monthly revenue

Displays data in bar and line charts using Chart.js.

