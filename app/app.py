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
    
    # Import and register all models with SQLAlchemy
    from app.models import init_models
    init_models()
    
    # Register blueprints
    from app.routes import events as events_bp
    from app.routes import participants as participants_bp
    from app.routes import teams as teams_bp
    from app.routes import checkin as checkin_bp
    from app.routes import tickets as tickets_bp
    from app.routes import emails as emails_bp
    from app.routes import admin as admin_bp
    from app.routes import reports as reports_bp
    from app.routes import csv_import as csv_bp
    from app.routes import frontend as frontend_bp
    from app.routes import auth as auth_bp
    from app.routes import api_docs as api_docs_bp
    from app.routes import email_templates as email_templates_bp
    from app.routes import stats as stats_bp
    from app.routes import smtp as smtp_bp
    from app.routes import invitations as invitations_bp

    app.register_blueprint(events_bp.bp)
    app.register_blueprint(participants_bp.bp)
    app.register_blueprint(teams_bp.bp)
    app.register_blueprint(checkin_bp.bp)
    app.register_blueprint(tickets_bp.bp)
    app.register_blueprint(emails_bp.bp)
    app.register_blueprint(admin_bp.bp)
    app.register_blueprint(reports_bp.bp)
    app.register_blueprint(csv_bp.bp)
    app.register_blueprint(frontend_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(api_docs_bp.bp, url_prefix='/api')
    app.register_blueprint(api_docs_bp.swaggerui_blueprint, url_prefix=api_docs_bp.SWAGGER_URL)
    app.register_blueprint(email_templates_bp.bp)
    app.register_blueprint(stats_bp.bp)
    app.register_blueprint(smtp_bp.bp)
    app.register_blueprint(invitations_bp.bp)

    # Register CLI commands
    from app.cli import register_commands
    register_commands(app)
    
    # Error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # Add cache-busting headers for development
    if app.config['DEBUG']:
        @app.after_request
        def add_header(response):
            """Add headers to prevent caching in development"""
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
            return response

    return app
