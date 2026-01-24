"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from app.config import config
from app.models import db, migrate


mail = Mail()


def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config['ALLOWED_ORIGINS'], supports_credentials=True)
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import events, auth
    
    # Register blueprints
    from app.routes import events as events_bp
    from app.routes import participants as participants_bp
    from app.routes import teams as teams_bp
    from app.routes import checkin as checkin_bp
    from app.routes import tickets as tickets_bp
    from app.routes import emails as emails_bp
    from app.routes import admin as admin_bp
    from app.routes import reports as reports_bp
    
    app.register_blueprint(events_bp.bp)
    app.register_blueprint(participants_bp.bp)
    app.register_blueprint(teams_bp.bp)
    app.register_blueprint(checkin_bp.bp)
    app.register_blueprint(tickets_bp.bp)
    app.register_blueprint(emails_bp.bp)
    app.register_blueprint(admin_bp.bp)
    app.register_blueprint(reports_bp.bp)
    
    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    return app
