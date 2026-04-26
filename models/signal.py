"""Traffic Signal model for signal management."""
from db import execute_query


class Signal:
    """Traffic Signal model class."""
    
    @staticmethod
    def get_all(status=None):
        """Get all traffic signals."""
        if status:
            return execute_query(
                "SELECT * FROM traffic_signals WHERE status = %s ORDER BY signal_code",
                (status,), fetch_all=True
            )
        return execute_query("SELECT * FROM traffic_signals ORDER BY signal_code", fetch_all=True)
    
    @staticmethod
    def get_by_id(signal_id):
        """Get signal by ID."""
        return execute_query("SELECT * FROM traffic_signals WHERE id = %s", (signal_id,), fetch_one=True)
    
    @staticmethod
    def get_count(status=None):
        """Get signal count."""
        if status:
            result = execute_query("SELECT COUNT(*) as count FROM traffic_signals WHERE status = %s", (status,), fetch_one=True)
        else:
            result = execute_query("SELECT COUNT(*) as count FROM traffic_signals", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def get_status_counts():
        """Get signal counts by status."""
        return execute_query(
            "SELECT status, COUNT(*) as count FROM traffic_signals GROUP BY status",
            fetch_all=True
        )
    
    @staticmethod
    def create(signal_code, location, intersection=None, status='active', signal_type='standard', installed_date=None):
        """Create a new traffic signal."""
        return execute_query(
            "INSERT INTO traffic_signals (signal_code, location, intersection, status, signal_type, installed_date) VALUES (%s,%s,%s,%s,%s,%s)",
            (signal_code, location, intersection, status, signal_type, installed_date),
            return_lastrowid=True
        )
    
    @staticmethod
    def update(signal_id, signal_code, location, intersection=None, status='active', signal_type='standard', installed_date=None, last_maintenance=None):
        """Update signal details."""
        execute_query(
            """UPDATE traffic_signals SET signal_code=%s, location=%s, intersection=%s, 
               status=%s, signal_type=%s, installed_date=%s, last_maintenance=%s WHERE id=%s""",
            (signal_code, location, intersection, status, signal_type, installed_date, last_maintenance, signal_id)
        )
    
    @staticmethod
    def update_status(signal_id, status):
        """Update signal status."""
        execute_query("UPDATE traffic_signals SET status = %s WHERE id = %s", (status, signal_id))
    
    @staticmethod
    def delete(signal_id):
        """Delete a traffic signal."""
        execute_query("DELETE FROM traffic_signals WHERE id = %s", (signal_id,))
