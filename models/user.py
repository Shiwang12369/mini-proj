"""User model for authentication and authorization."""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from db import execute_query


class User(UserMixin):
    """User model class."""
    
    def __init__(self, id, username, password_hash, role, full_name, email, badge_number, is_active, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.badge_number = badge_number
        self._is_active = is_active
        self.created_at = created_at
    
    @property
    def is_active(self):
        return self._is_active
    
    @staticmethod
    def from_dict(data):
        """Create User from dictionary."""
        if not data:
            return None
        return User(
            id=data['id'],
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            full_name=data['full_name'],
            email=data.get('email'),
            badge_number=data.get('badge_number'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at')
        )
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        data = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
        return User.from_dict(data)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        data = execute_query("SELECT * FROM users WHERE username = %s", (username,), fetch_one=True)
        return User.from_dict(data)
    
    @staticmethod
    def create(username, password, role, full_name, email=None, badge_number=None):
        """Create a new user."""
        password_hash = generate_password_hash(password)
        user_id = execute_query(
            "INSERT INTO users (username, password_hash, role, full_name, email, badge_number) VALUES (%s, %s, %s, %s, %s, %s)",
            (username, password_hash, role, full_name, email, badge_number),
            return_lastrowid=True
        )
        return user_id
    
    @staticmethod
    def update(user_id, full_name, email=None, badge_number=None, role=None):
        """Update user details."""
        execute_query(
            "UPDATE users SET full_name = %s, email = %s, badge_number = %s, role = %s WHERE id = %s",
            (full_name, email, badge_number, role, user_id)
        )
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password."""
        password_hash = generate_password_hash(new_password)
        execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
    
    @staticmethod
    def get_all():
        """Get all users."""
        return execute_query("SELECT id, username, role, full_name, email, badge_number, is_active, created_at FROM users ORDER BY created_at DESC", fetch_all=True)
    
    def verify_password(self, password):
        """Check if the provided password matches."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def ensure_admin():
        """Ensure default admin exists with correct password."""
        admin = User.get_by_username('admin')
        if not admin:
            User.create('admin', 'admin123', 'admin', 'System Administrator', 'admin@tms.local', 'ADM-001')
        elif not admin.verify_password('admin123'):
            User.update_password(admin.id, 'admin123')
