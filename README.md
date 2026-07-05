Hospital Management System (HMS)
A clean, console-based Hospital Management System implemented in Python utilizing Object-Oriented Programming (OOP) principles and backed by a MySQL database. Designed to be completely modular and follow professional software development practices.

Features
Role-Based Login: Dedicated access profiles for Admin, Doctor, and Receptionist roles.
Patient Management: Complete CRUD operations, input checking, and unique business ID generation (PAT-10001).
Doctor Management: Registers professional details and generates user credentials dynamically in transactions.
Appointment Scheduling: Real-time slot checks to prevent doctor double-booking.
Billing & Payments: Invoicing, partial/full payment tracking, auto-calculated balances.
Pharmacy Inventory: Tracks medicine stock and flags low inventory or expired batches.
Reports & Analytics: Daily registrations, daily revenue aggregation, doctor schedule timelines, and pharmacy audit reports.
Directory Structure
text

Hospital_Management_System/
├── config.py             # Database server credentials & formats
├── database.py           # MySQL connector operations & schema executor
├── main.py               # Main CLI app loop & console view router
├── README.md             # Documentation and usage guide
├── sql/
│   └── schema.sql        # Database tables & testing seeds
├── models/
│   ├── user.py           # User credential data container
│   ├── patient.py        # Patient demographic record class
│   ├── doctor.py         # Doctor credentials and specialization mapping
│   ├── appointment.py    # Appointment schedule class
│   ├── bill.py           # Financial transaction invoice class
│   └── medicine.py       # Pharmacy stock item class
├── services/
│   ├── auth_service.py   # Login logic and password verification
│   ├── patient_service.py# Patient data validation & CRUD
│   ├── doctor_service.py # Transactional registration of Doctor accounts
│   ├── appt_service.py   # Scheduling slot verification & management
│   ├── bill_service.py   # Financial billing calculations
│   ├── pharmacy_service.py# Inventory tracking & pricing
│   └── report_service.py # Aggregate metrics & analytics reports
├── utils/
│   ├── validators.py     # Static input validation functions
│   └── helpers.py        # SHA-256 Hashing, CLI formatting, & ID generators
└── tests/
    └── test_system.py    # Unit tests for business utilities
Installation & Configuration
Prerequisites
Python 3.8+
MySQL Server (ensure it is running locally or remotely)
Python library: mysql-connector-python
Install dependencies:

bash

pip install mysql-connector-python
Database Settings
Open 
config.py
 and update the server configuration with your local MySQL password:

python

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_actual_mysql_password_here"  # Update this line
DB_NAME = "hospital_db"
DB_PORT = 3306
Initialization & Running
Run the application from the project root directory. On the first startup, the database hospital_db and all schema tables will be automatically created and populated with demo seed data:

bash

python main.py
Default Login Credentials
Use the following seeded accounts to test the HMS features:

Username	Password	Role
admin	admin123	Admin
receptionist	rec123	Receptionist
drsmith	doc123	Doctor
Running Unit Tests
Execute the unit tests suite to verify validator logic and OOP models:

bash

python -m unittest tests/test_system.py