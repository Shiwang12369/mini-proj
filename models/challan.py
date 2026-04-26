"""Challan model for fine/ticket management."""
import random
import string
from datetime import datetime, timedelta
from db import execute_query


class Challan:
    """Challan (Fine/Ticket) model class."""
    
    @staticmethod
    def generate_challan_number():
        """Generate a unique challan number."""
        prefix = "TMS"
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}-{date_part}-{random_part}"
    
    @staticmethod
    def get_all(status=None, search=None, date_from=None, date_to=None):
        """Get all challans with optional filters."""
        query = """SELECT c.*, v.registration_number, v.vehicle_type, v.make, v.model as vehicle_model,
                   vio.violation_code, vio.description as violation_desc, vio.severity,
                   u.full_name as officer_name, ts.signal_code, ts.location as signal_location,
                   o.name as owner_name, o.phone as owner_phone
                   FROM challans c
                   JOIN vehicles v ON c.vehicle_id = v.id
                   LEFT JOIN owners o ON v.owner_id = o.id
                   JOIN violations vio ON c.violation_id = vio.id
                   LEFT JOIN users u ON c.issued_by = u.id
                   LEFT JOIN traffic_signals ts ON c.signal_id = ts.id
                   WHERE 1=1"""
        params = []
        
        if status:
            query += " AND c.status = %s"
            params.append(status)
        
        if search:
            query += " AND (c.challan_number LIKE %s OR v.registration_number LIKE %s OR o.name LIKE %s)"
            s = f"%{search}%"
            params.extend([s, s, s])
        
        if date_from:
            query += " AND DATE(c.date_issued) >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND DATE(c.date_issued) <= %s"
            params.append(date_to)
        
        query += " ORDER BY c.date_issued DESC"
        return execute_query(query, tuple(params), fetch_all=True)
    
    @staticmethod
    def get_by_id(challan_id):
        """Get challan by ID with full details."""
        return execute_query(
            """SELECT c.*, v.registration_number, v.vehicle_type, v.make, v.model as vehicle_model, v.color,
               vio.violation_code, vio.description as violation_desc, vio.severity, vio.points,
               u.full_name as officer_name, u.badge_number,
               ts.signal_code, ts.location as signal_location,
               o.name as owner_name, o.phone as owner_phone, o.email as owner_email, o.address as owner_address
               FROM challans c
               JOIN vehicles v ON c.vehicle_id = v.id
               LEFT JOIN owners o ON v.owner_id = o.id
               JOIN violations vio ON c.violation_id = vio.id
               LEFT JOIN users u ON c.issued_by = u.id
               LEFT JOIN traffic_signals ts ON c.signal_id = ts.id
               WHERE c.id = %s""",
            (challan_id,), fetch_one=True
        )
    
    @staticmethod
    def get_count(status=None):
        """Get challan count, optionally filtered by status."""
        if status:
            result = execute_query("SELECT COUNT(*) as count FROM challans WHERE status = %s", (status,), fetch_one=True)
        else:
            result = execute_query("SELECT COUNT(*) as count FROM challans", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def get_total_revenue():
        """Get total revenue from paid challans."""
        result = execute_query(
            "SELECT COALESCE(SUM(fine_amount), 0) as total FROM challans WHERE status = 'paid'",
            fetch_one=True
        )
        return float(result['total']) if result else 0
    
    @staticmethod
    def get_pending_amount():
        """Get total pending fine amount."""
        result = execute_query(
            "SELECT COALESCE(SUM(fine_amount), 0) as total FROM challans WHERE status IN ('pending', 'overdue')",
            fetch_one=True
        )
        return float(result['total']) if result else 0
    
    @staticmethod
    def get_monthly_stats(months=6):
        """Get monthly challan statistics."""
        return execute_query(
            "SELECT strftime('%Y-%m', date_issued) as month,"
            " COUNT(*) as total_challans,"
            " SUM(CASE WHEN status = 'paid' THEN fine_amount ELSE 0 END) as revenue,"
            " SUM(fine_amount) as total_fines"
            " FROM challans"
            " WHERE date_issued >= date('now', '-' || ? || ' months')"
            " GROUP BY strftime('%Y-%m', date_issued)"
            " ORDER BY month",
            (months,), fetch_all=True
        )
    
    @staticmethod
    def get_violation_distribution():
        """Get challan distribution by violation type."""
        return execute_query(
            """SELECT vio.description, vio.severity, COUNT(*) as count 
               FROM challans c JOIN violations vio ON c.violation_id = vio.id
               GROUP BY vio.id, vio.description, vio.severity ORDER BY count DESC LIMIT 10""",
            fetch_all=True
        )
    
    @staticmethod
    def get_status_distribution():
        """Get challan distribution by status."""
        return execute_query(
            "SELECT status, COUNT(*) as count FROM challans GROUP BY status",
            fetch_all=True
        )
    
    @staticmethod
    def get_recent(limit=10):
        """Get recent challans."""
        return execute_query(
            """SELECT c.*, v.registration_number, vio.description as violation_desc, vio.severity,
               u.full_name as officer_name, o.name as owner_name
               FROM challans c
               JOIN vehicles v ON c.vehicle_id = v.id
               LEFT JOIN owners o ON v.owner_id = o.id
               JOIN violations vio ON c.violation_id = vio.id
               LEFT JOIN users u ON c.issued_by = u.id
               ORDER BY c.date_issued DESC LIMIT %s""",
            (limit,), fetch_all=True
        )
    
    @staticmethod
    def create(vehicle_id, violation_id, issued_by, fine_amount, location=None, signal_id=None, description=None, remarks=None):
        """Create a new challan."""
        challan_number = Challan.generate_challan_number()
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        return execute_query(
            """INSERT INTO challans (challan_number, vehicle_id, violation_id, issued_by, signal_id, location,
               description, fine_amount, due_date, remarks, status) 
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending')""",
            (challan_number, vehicle_id, violation_id, issued_by, signal_id or None, location, description, fine_amount, due_date, remarks),
            return_lastrowid=True
        )
    
    @staticmethod
    def update_status(challan_id, status):
        """Update challan status."""
        paid_date = datetime.now().strftime('%Y-%m-%d') if status == 'paid' else None
        execute_query(
            "UPDATE challans SET status = %s, paid_date = %s WHERE id = %s",
            (status, paid_date, challan_id)
        )
    
    @staticmethod
    def update_overdue():
        """Mark overdue challans."""
        execute_query(
            "UPDATE challans SET status = 'overdue' WHERE status = 'pending' AND due_date < CURDATE()"
        )
