"""Violation model for traffic violation type management."""
from db import execute_query


class Violation:
    """Violation model class."""
    
    @staticmethod
    def get_all(severity=None):
        """Get all violation types."""
        if severity:
            return execute_query(
                "SELECT * FROM violations WHERE severity = %s ORDER BY fine_amount DESC",
                (severity,), fetch_all=True
            )
        return execute_query("SELECT * FROM violations ORDER BY fine_amount DESC", fetch_all=True)
    
    @staticmethod
    def get_active():
        """Get all active violations."""
        return execute_query("SELECT * FROM violations WHERE is_active = TRUE ORDER BY violation_code", fetch_all=True)
    
    @staticmethod
    def get_by_id(violation_id):
        """Get violation by ID."""
        return execute_query("SELECT * FROM violations WHERE id = %s", (violation_id,), fetch_one=True)
    
    @staticmethod
    def get_count():
        """Get total violation type count."""
        result = execute_query("SELECT COUNT(*) as count FROM violations", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def create(violation_code, description, fine_amount, severity='medium', points=0):
        """Create a new violation type."""
        return execute_query(
            "INSERT INTO violations (violation_code, description, fine_amount, severity, points) VALUES (%s,%s,%s,%s,%s)",
            (violation_code, description, fine_amount, severity, points),
            return_lastrowid=True
        )
    
    @staticmethod
    def update(violation_id, violation_code, description, fine_amount, severity='medium', points=0):
        """Update violation type."""
        execute_query(
            "UPDATE violations SET violation_code=%s, description=%s, fine_amount=%s, severity=%s, points=%s WHERE id=%s",
            (violation_code, description, fine_amount, severity, points, violation_id)
        )
    
    @staticmethod
    def toggle_active(violation_id):
        """Toggle active status."""
        execute_query("UPDATE violations SET is_active = NOT is_active WHERE id = %s", (violation_id,))
