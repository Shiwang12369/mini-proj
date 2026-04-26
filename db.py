"""Database connection manager using SQLite (zero-config, no install needed)."""
import sqlite3
import os
from config import Config

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'traffic_management.db')


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def dict_from_row(row):
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    return dict(row)


def init_db():
    """Initialize the database - create tables and seed data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'officer' CHECK(role IN ('admin', 'officer')),
                full_name TEXT NOT NULL,
                email TEXT,
                badge_number TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS owners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                address TEXT,
                license_number TEXT UNIQUE,
                date_of_birth TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_number TEXT NOT NULL UNIQUE,
                vehicle_type TEXT NOT NULL DEFAULT 'car' CHECK(vehicle_type IN ('car', 'bike', 'truck', 'bus', 'auto', 'other')),
                make TEXT,
                model TEXT,
                color TEXT,
                year INTEGER,
                owner_id INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES owners(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                violation_code TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                fine_amount REAL NOT NULL,
                severity TEXT NOT NULL DEFAULT 'medium' CHECK(severity IN ('low', 'medium', 'high', 'critical')),
                points INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS traffic_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_code TEXT NOT NULL UNIQUE,
                location TEXT NOT NULL,
                intersection TEXT,
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'maintenance')),
                signal_type TEXT DEFAULT 'standard' CHECK(signal_type IN ('standard', 'pedestrian', 'flashing', 'smart')),
                installed_date TEXT,
                last_maintenance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challan_number TEXT NOT NULL UNIQUE,
                vehicle_id INTEGER NOT NULL,
                violation_id INTEGER NOT NULL,
                issued_by INTEGER,
                signal_id INTEGER,
                location TEXT,
                description TEXT,
                fine_amount REAL NOT NULL,
                date_issued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TEXT,
                paid_date TEXT,
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'overdue', 'disputed', 'cancelled')),
                remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
                FOREIGN KEY (violation_id) REFERENCES violations(id) ON DELETE RESTRICT,
                FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (signal_id) REFERENCES traffic_signals(id) ON DELETE SET NULL
            );
        """)
        
        # Seed violation types (only if empty)
        cursor.execute("SELECT COUNT(*) FROM violations")
        if cursor.fetchone()[0] == 0:
            violations_data = [
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
                ('V015', 'Illegal Modification', 1500.00, 'medium', 2),
            ]
            cursor.executemany(
                "INSERT INTO violations (violation_code, description, fine_amount, severity, points) VALUES (?,?,?,?,?)",
                violations_data
            )
        
        # Seed traffic signals (only if empty)
        cursor.execute("SELECT COUNT(*) FROM traffic_signals")
        if cursor.fetchone()[0] == 0:
            signals_data = [
                ('SIG-001', 'MG Road & Park Street', 'MG Road Junction', 'active', 'smart', '2023-01-15'),
                ('SIG-002', 'Station Road & NH-48', 'Station Crossing', 'active', 'standard', '2022-06-20'),
                ('SIG-003', 'Mall Road & Ring Road', 'Mall Road Circle', 'active', 'standard', '2023-03-10'),
                ('SIG-004', 'University Road & Civil Lines', 'University Gate', 'maintenance', 'pedestrian', '2021-11-05'),
                ('SIG-005', 'Industrial Area Phase-1', 'Factory Junction', 'active', 'flashing', '2024-02-28'),
            ]
            cursor.executemany(
                "INSERT INTO traffic_signals (signal_code, location, intersection, status, signal_type, installed_date) VALUES (?,?,?,?,?,?)",
                signals_data
            )
        
        # Seed owners (only if empty)
        cursor.execute("SELECT COUNT(*) FROM owners")
        if cursor.fetchone()[0] == 0:
            owners_data = [
                ('Rahul Sharma', '9876543210', 'rahul@email.com', '123 MG Road, Delhi', 'DL-0420110012345', '1990-05-15'),
                ('Priya Singh', '9876543211', 'priya@email.com', '456 Park Street, Mumbai', 'MH-0120120067890', '1992-08-22'),
                ('Amit Patel', '9876543212', 'amit@email.com', '789 Station Road, Ahmedabad', 'GJ-0120130011111', '1988-12-01'),
                ('Sneha Gupta', '9876543213', 'sneha@email.com', '101 Civil Lines, Jaipur', 'RJ-1420140022222', '1995-03-30'),
                ('Vikram Joshi', '9876543214', 'vikram@email.com', '202 Ring Road, Pune', 'MH-1220150033333', '1985-07-10'),
            ]
            cursor.executemany(
                "INSERT INTO owners (name, phone, email, address, license_number, date_of_birth) VALUES (?,?,?,?,?,?)",
                owners_data
            )
        
        # Seed vehicles (only if empty)
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        if cursor.fetchone()[0] == 0:
            vehicles_data = [
                ('DL-01-AB-1234', 'car', 'Maruti Suzuki', 'Swift', 'White', 2022, 1),
                ('MH-01-CD-5678', 'bike', 'Honda', 'Activa 6G', 'Black', 2023, 2),
                ('GJ-01-EF-9012', 'truck', 'Tata', 'Ace Gold', 'Blue', 2021, 3),
                ('RJ-14-GH-3456', 'car', 'Hyundai', 'Creta', 'Red', 2024, 4),
                ('MH-12-IJ-7890', 'bus', 'Ashok Leyland', 'Viking', 'Yellow', 2020, 5),
                ('DL-01-KL-1111', 'auto', 'Bajaj', 'RE Compact', 'Green', 2023, 1),
                ('MH-01-MN-2222', 'bike', 'Royal Enfield', 'Classic 350', 'Grey', 2024, 2),
            ]
            cursor.executemany(
                "INSERT INTO vehicles (registration_number, vehicle_type, make, model, color, year, owner_id) VALUES (?,?,?,?,?,?,?)",
                vehicles_data
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("[OK] Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database initialization error: {e}")
        return False


def execute_query(query, params=None, fetch_one=False, fetch_all=False, return_lastrowid=False):
    """Execute a query and return results.
    
    Automatically converts MySQL-style %s placeholders to SQLite ? placeholders.
    """
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Convert MySQL %s placeholders to SQLite ?
        if query:
            query = query.replace('%s', '?')
            # Convert MySQL-specific functions
            query = query.replace('CURDATE()', "date('now')")
            query = query.replace('NOW()', "datetime('now')")
        
        cursor.execute(query, params or ())
        
        if fetch_one:
            row = cursor.fetchone()
            result = dict_from_row(row)
        elif fetch_all:
            rows = cursor.fetchall()
            result = [dict_from_row(r) for r in rows]
        elif return_lastrowid:
            conn.commit()
            result = cursor.lastrowid
        else:
            conn.commit()
            result = cursor.rowcount
        
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
