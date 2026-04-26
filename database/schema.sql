-- =====================================================
-- Traffic Management System - Database Schema
-- =====================================================

CREATE DATABASE IF NOT EXISTS traffic_management;
USE traffic_management;

-- =====================================================
-- Users Table (Admin / Officers)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'officer') NOT NULL DEFAULT 'officer',
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    badge_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Owners Table (Vehicle Owners)
-- =====================================================
CREATE TABLE IF NOT EXISTS owners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    address TEXT,
    license_number VARCHAR(20) UNIQUE,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Vehicles Table
-- =====================================================
CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_type ENUM('car', 'bike', 'truck', 'bus', 'auto', 'other') NOT NULL DEFAULT 'car',
    make VARCHAR(50),
    model VARCHAR(50),
    color VARCHAR(30),
    year INT,
    owner_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE SET NULL
);

-- =====================================================
-- Violations Table (Types of Violations)
-- =====================================================
CREATE TABLE IF NOT EXISTS violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    violation_code VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    fine_amount DECIMAL(10, 2) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
    points INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Traffic Signals Table
-- =====================================================
CREATE TABLE IF NOT EXISTS traffic_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    signal_code VARCHAR(20) NOT NULL UNIQUE,
    location VARCHAR(255) NOT NULL,
    intersection VARCHAR(255),
    status ENUM('active', 'inactive', 'maintenance') NOT NULL DEFAULT 'active',
    signal_type ENUM('standard', 'pedestrian', 'flashing', 'smart') DEFAULT 'standard',
    installed_date DATE,
    last_maintenance DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- Challans Table (Fines / Tickets)
-- =====================================================
CREATE TABLE IF NOT EXISTS challans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challan_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_id INT NOT NULL,
    violation_id INT NOT NULL,
    issued_by INT,
    signal_id INT,
    location VARCHAR(255),
    description TEXT,
    fine_amount DECIMAL(10, 2) NOT NULL,
    date_issued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    paid_date DATE,
    status ENUM('pending', 'paid', 'overdue', 'disputed', 'cancelled') NOT NULL DEFAULT 'pending',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    FOREIGN KEY (violation_id) REFERENCES violations(id) ON DELETE RESTRICT,
    FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (signal_id) REFERENCES traffic_signals(id) ON DELETE SET NULL
);

-- =====================================================
-- Indexes for Performance
-- =====================================================
CREATE INDEX idx_vehicles_reg ON vehicles(registration_number);
CREATE INDEX idx_challans_status ON challans(status);
CREATE INDEX idx_challans_date ON challans(date_issued);
CREATE INDEX idx_challans_vehicle ON challans(vehicle_id);
CREATE INDEX idx_owners_license ON owners(license_number);
CREATE INDEX idx_owners_phone ON owners(phone);

-- =====================================================
-- Seed Data: Default Admin User
-- Password: admin123 (hashed with werkzeug)
-- =====================================================
INSERT INTO users (username, password_hash, role, full_name, email, badge_number) VALUES
('admin', 'scrypt:32768:8:1$placeholder$placeholder', 'admin', 'System Administrator', 'admin@tms.local', 'ADM-001');

-- =====================================================
-- Seed Data: Violation Types
-- =====================================================
INSERT INTO violations (violation_code, description, fine_amount, severity, points) VALUES
('V001', 'Over Speeding', 1000.00, 'high', 3),
('V002', 'Signal Jumping (Red Light)', 2000.00, 'critical', 4),
('V003', 'Driving Without License', 5000.00, 'critical', 6),
('V004', 'Driving Without Seatbelt', 500.00, 'low', 1),
('V005', 'Using Mobile While Driving', 1500.00, 'high', 3),
('V006', 'Wrong Side Driving', 2000.00, 'critical', 4),
('V007', 'Parking Violation', 500.00, 'low', 1),
('V008', 'No Helmet (Two-Wheeler)', 1000.00, 'medium', 2),
('V009', 'Drunk Driving', 10000.00, 'critical', 6),
('V010', 'Overloading', 2000.00, 'high', 3),
('V011', 'Expired Registration', 2500.00, 'medium', 2),
('V012', 'No Insurance', 3000.00, 'high', 3),
('V013', 'Reckless Driving', 5000.00, 'critical', 5),
('V014', 'No Pollution Certificate', 1000.00, 'medium', 2),
('V015', 'Illegal Modification', 1500.00, 'medium', 2);

-- =====================================================
-- Seed Data: Sample Traffic Signals
-- =====================================================
INSERT INTO traffic_signals (signal_code, location, intersection, status, signal_type, installed_date) VALUES
('SIG-001', 'MG Road & Park Street', 'MG Road Junction', 'active', 'smart', '2023-01-15'),
('SIG-002', 'Station Road & NH-48', 'Station Crossing', 'active', 'standard', '2022-06-20'),
('SIG-003', 'Mall Road & Ring Road', 'Mall Road Circle', 'active', 'standard', '2023-03-10'),
('SIG-004', 'University Road & Civil Lines', 'University Gate', 'maintenance', 'pedestrian', '2021-11-05'),
('SIG-005', 'Industrial Area Phase-1', 'Factory Junction', 'active', 'flashing', '2024-02-28');

-- =====================================================
-- Seed Data: Sample Owners
-- =====================================================
INSERT INTO owners (name, phone, email, address, license_number, date_of_birth) VALUES
('Rahul Sharma', '9876543210', 'rahul@email.com', '123 MG Road, Delhi', 'DL-0420110012345', '1990-05-15'),
('Priya Singh', '9876543211', 'priya@email.com', '456 Park Street, Mumbai', 'MH-0120120067890', '1992-08-22'),
('Amit Patel', '9876543212', 'amit@email.com', '789 Station Road, Ahmedabad', 'GJ-0120130011111', '1988-12-01'),
('Sneha Gupta', '9876543213', 'sneha@email.com', '101 Civil Lines, Jaipur', 'RJ-1420140022222', '1995-03-30'),
('Vikram Joshi', '9876543214', 'vikram@email.com', '202 Ring Road, Pune', 'MH-1220150033333', '1985-07-10');

-- =====================================================
-- Seed Data: Sample Vehicles
-- =====================================================
INSERT INTO vehicles (registration_number, vehicle_type, make, model, color, year, owner_id) VALUES
('DL-01-AB-1234', 'car', 'Maruti Suzuki', 'Swift', 'White', 2022, 1),
('MH-01-CD-5678', 'bike', 'Honda', 'Activa 6G', 'Black', 2023, 2),
('GJ-01-EF-9012', 'truck', 'Tata', 'Ace Gold', 'Blue', 2021, 3),
('RJ-14-GH-3456', 'car', 'Hyundai', 'Creta', 'Red', 2024, 4),
('MH-12-IJ-7890', 'bus', 'Ashok Leyland', 'Viking', 'Yellow', 2020, 5),
('DL-01-KL-1111', 'auto', 'Bajaj', 'RE Compact', 'Green', 2023, 1),
('MH-01-MN-2222', 'bike', 'Royal Enfield', 'Classic 350', 'Grey', 2024, 2);
