-- Hospital Management System - Database Schema Initialization
-- Target Database: MySQL
CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;
-- 1. Users Table (Authentication & Access Control)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL, -- SHA-256 hash length is 64 hex characters
    role ENUM('Admin', 'Doctor', 'Receptionist') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- 2. Patients Table (Demographics & Medical Record reference)
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(20) PRIMARY KEY, -- Formatted as PAT-XXXXX
    name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- 3. Doctors Table (Profiles and Specialization)
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id VARCHAR(20) PRIMARY KEY, -- Formatted as DOC-XXXXX
    user_id INT UNIQUE, -- One-to-one relationship with user credentials (if login is allowed)
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    qualification VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;
-- 4. Appointments Table (Scheduling & Status Tracking)
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id VARCHAR(20) PRIMARY KEY, -- Formatted as APT-XXXXX
    patient_id VARCHAR(20) NOT NULL,
    doctor_id VARCHAR(20) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
) ENGINE=InnoDB;
-- 5. Bills Table (Patient Billing and Invoicing)
CREATE TABLE IF NOT EXISTS bills (
    bill_id VARCHAR(20) PRIMARY KEY, -- Formatted as BIL-XXXXX
    patient_id VARCHAR(20) NOT NULL,
    appointment_id VARCHAR(20) UNIQUE, -- One bill per appointment (nullable if direct billing)
    total_amount DECIMAL(10, 2) NOT NULL,
    paid_amount DECIMAL(10, 2) DEFAULT 0.00,
    balance_amount DECIMAL(10, 2) NOT NULL, -- Calculated in service: total - paid
    payment_status ENUM('Unpaid', 'Partially Paid', 'Paid') DEFAULT 'Unpaid',
    billing_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
) ENGINE=InnoDB;
-- 6. Medicines Table (Pharmacy Inventory)
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    manufacturer VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    expiry_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- =========================================================================
-- SEED DATA FOR TESTING
-- =========================================================================
-- Hash for password 'admin123' (SHA-256): 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
-- Hash for password 'rec123' (SHA-256): 1270ddbd388e309b1234f4e500ea78a83c9d111040fa6cce86c31df0144a3659
-- Hash for password 'doc123' (SHA-256): c3362e4da49c24d379b72152ae6c99f1fa035f52829dceed715a7bf8bb464b98
INSERT IGNORE INTO users (user_id, username, password_hash, role) VALUES
(1, 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Admin'),
(2, 'receptionist', '1270ddbd388e309b1234f4e500ea78a83c9d111040fa6cce86c31df0144a3659', 'Receptionist'),
(3, 'drsmith', 'c3362e4da49c24d379b72152ae6c99f1fa035f52829dceed715a7bf8bb464b98', 'Doctor');
-- Seed a doctor connected to user 3
INSERT IGNORE INTO doctors (doctor_id, user_id, name, specialization, phone, email, qualification) VALUES
('DOC-10001', 3, 'Dr. John Smith', 'Cardiology', '9876543210', 'john.smith@hospital.com', 'MD, DM');
-- Seed sample patients
INSERT IGNORE INTO patients (patient_id, name, dob, gender, phone, email, address) VALUES
('PAT-10001', 'Alice Brown', '1990-05-15', 'Female', '9500012345', 'alice@email.com', '123 Main St, Springfield'),
('PAT-10002', 'Bob Geldoff', '1985-11-20', 'Male', '9500054321', 'bob@email.com', '456 Elm St, Springfield');
-- Seed sample medicines
INSERT IGNORE INTO medicines (name, manufacturer, price, stock_quantity, expiry_date) VALUES
('Paracetamol 500mg', 'GSK', 1.50, 200, '2028-12-31'),
('Amoxicillin 250mg', 'Sandoz', 12.00, 50, '2027-06-30'),
('Ibuprofen 400mg', 'Pfizer', 3.20, 150, '2028-09-15');
