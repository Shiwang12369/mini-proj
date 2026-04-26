"""
Traffic Management System
Main Flask Application Entry Point
"""
from datetime import datetime
from flask import Flask
from flask_login import LoginManager
from config import Config
from db import init_db
from models.user import User

# Import route blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.vehicles import vehicles_bp
from routes.owners import owners_bp
from routes.violations import violations_bp
from routes.challans import challans_bp
from routes.signals import signals_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access the Traffic Management System.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
    
    # Register Jinja2 template filters for date formatting (SQLite returns strings)
    @app.template_filter('format_date')
    def format_date(value, fmt='%d %b %Y'):
        """Format a date string to a readable format."""
        if not value:
            return '-'
        if isinstance(value, str):
            try:
                # Try common formats
                for parse_fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        dt = datetime.strptime(value.split('.')[0], parse_fmt)
                        return dt.strftime(fmt)
                    except ValueError:
                        continue
                return value
            except Exception:
                return value
        elif hasattr(value, 'strftime'):
            return value.strftime(fmt)
        return str(value)
    
    @app.template_filter('format_datetime')
    def format_datetime(value, fmt='%d %B %Y, %I:%M %p'):
        """Format a datetime string to a readable format."""
        return format_date(value, fmt)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(owners_bp)
    app.register_blueprint(violations_bp)
    app.register_blueprint(challans_bp)
    app.register_blueprint(signals_bp)
    
    return app


if __name__ == '__main__':
    # Initialize database
    print("[TMS] Traffic Management System")
    print("=" * 40)
    print("Initializing database...")
    
    if init_db():
        # Ensure default admin user exists
        try:
            User.ensure_admin()
            print("[OK] Default admin user ready (admin / admin123)")
        except Exception as e:
            print(f"[WARN] Admin user setup: {e}")
        
        app = create_app()
        print(f"\n[SERVER] Starting at http://localhost:{Config.PORT}")
        print(f"[LOGIN] admin / admin123")
        print("=" * 40)
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )
    else:
        print("\n[ERROR] Failed to initialize database.")
        print("Make sure SQLite database could not be created.")
        print("Check write permissions in the project directory.")
