"""
Database models initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Import all models to ensure they're registered with SQLAlchemy
# This is necessary for string-based relationship() references to work
def init_models():
    """Import all models to register them with SQLAlchemy"""
    from app.models.events import Event, Team, Participant, EmailLog, CheckinLog, CeleryJob
    from app.models.auth import Role, Permission, RolePermission, AdminUser
    
    # Return models for convenience
    return {
        'Event': Event,
        'Team': Team,
        'Participant': Participant,
        'EmailLog': EmailLog,
        'CheckinLog': CheckinLog,
        'CeleryJob': CeleryJob,
        'Role': Role,
        'Permission': Permission,
        'RolePermission': RolePermission,
        'AdminUser': AdminUser
    }
