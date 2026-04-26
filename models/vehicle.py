"""Vehicle model for vehicle management."""
from db import execute_query


class Vehicle:
    """Vehicle model class."""
    
    @staticmethod
    def get_all(search=None, vehicle_type=None):
        """Get all vehicles with optional filters."""
        query = """SELECT v.*, o.name as owner_name, o.phone as owner_phone
                   FROM vehicles v 
                   LEFT JOIN owners o ON v.owner_id = o.id
                   WHERE 1=1"""
        params = []
        
        if search:
            query += " AND (v.registration_number LIKE %s OR v.make LIKE %s OR v.model LIKE %s OR o.name LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if vehicle_type:
            query += " AND v.vehicle_type = %s"
            params.append(vehicle_type)
        
        query += " ORDER BY v.created_at DESC"
        return execute_query(query, tuple(params), fetch_all=True)
    
    @staticmethod
    def get_by_id(vehicle_id):
        """Get vehicle by ID with owner info."""
        return execute_query(
            """SELECT v.*, o.name as owner_name, o.phone as owner_phone, o.email as owner_email
               FROM vehicles v LEFT JOIN owners o ON v.owner_id = o.id WHERE v.id = %s""",
            (vehicle_id,), fetch_one=True
        )
    
    @staticmethod
    def get_by_registration(reg_number):
        """Get vehicle by registration number."""
        return execute_query(
            """SELECT v.*, o.name as owner_name, o.phone as owner_phone
               FROM vehicles v LEFT JOIN owners o ON v.owner_id = o.id
               WHERE v.registration_number = %s""",
            (reg_number,), fetch_one=True
        )
    
    @staticmethod
    def get_count():
        """Get total vehicle count."""
        result = execute_query("SELECT COUNT(*) as count FROM vehicles", fetch_one=True)
        return result['count'] if result else 0
    
    @staticmethod
    def get_type_stats():
        """Get vehicle count by type."""
        return execute_query(
            "SELECT vehicle_type, COUNT(*) as count FROM vehicles GROUP BY vehicle_type ORDER BY count DESC",
            fetch_all=True
        )
    
    @staticmethod
    def create(registration_number, vehicle_type, make=None, model=None, color=None, year=None, owner_id=None):
        """Create a new vehicle."""
        return execute_query(
            "INSERT INTO vehicles (registration_number, vehicle_type, make, model, color, year, owner_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (registration_number, vehicle_type, make, model, color, year, owner_id),
            return_lastrowid=True
        )
    
    @staticmethod
    def update(vehicle_id, registration_number, vehicle_type, make=None, model=None, color=None, year=None, owner_id=None):
        """Update vehicle details."""
        execute_query(
            "UPDATE vehicles SET registration_number=%s, vehicle_type=%s, make=%s, model=%s, color=%s, year=%s, owner_id=%s WHERE id=%s",
            (registration_number, vehicle_type, make, model, color, year, owner_id, vehicle_id)
        )
    
    @staticmethod
    def delete(vehicle_id):
        """Delete a vehicle."""
        execute_query("DELETE FROM vehicles WHERE id = %s", (vehicle_id,))
