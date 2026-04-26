"""Owner model for vehicle owner management."""
from db import execute_query


class Owner:
    """Owner model class."""
    
    @staticmethod
    def get_all(search=None):
        """Get all owners with optional search."""
        if search:
            query = """SELECT * FROM owners 
                       WHERE name LIKE %s OR phone LIKE %s OR license_number LIKE %s OR email LIKE %s
                       ORDER BY created_at DESC"""
            search_param = f"%{search}%"
            return execute_query(query, (search_param, search_param, search_param, search_param), fetch_all=True)
        return execute_query("SELECT * FROM owners ORDER BY created_at DESC", fetch_all=True)
    
    @staticmethod
    def get_by_id(owner_id):
        """Get owner by ID."""
        return execute_query("SELECT * FROM owners WHERE id = %s", (owner_id,), fetch_one=True)
    
    @staticmethod
    def get_count():
        """Get total owner count."""
        result = execute_query("SELECT COUNT(*) as count FROM owners", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def create(name, phone, email=None, address=None, license_number=None, date_of_birth=None):
        """Create a new owner."""
        return execute_query(
            "INSERT INTO owners (name, phone, email, address, license_number, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, phone, email, address, license_number, date_of_birth),
            return_lastrowid=True
        )
    
    @staticmethod
    def update(owner_id, name, phone, email=None, address=None, license_number=None, date_of_birth=None):
        """Update owner details."""
        execute_query(
            "UPDATE owners SET name=%s, phone=%s, email=%s, address=%s, license_number=%s, date_of_birth=%s WHERE id=%s",
            (name, phone, email, address, license_number, date_of_birth, owner_id)
        )
    
    @staticmethod
    def delete(owner_id):
        """Delete an owner."""
        execute_query("DELETE FROM owners WHERE id = %s", (owner_id,))
    
    @staticmethod
    def get_vehicles(owner_id):
        """Get all vehicles belonging to an owner."""
        return execute_query("SELECT * FROM vehicles WHERE owner_id = %s", (owner_id,), fetch_all=True)
