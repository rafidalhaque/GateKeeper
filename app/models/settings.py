"""
Application settings model for storing configuration
"""
from app.models import db
from datetime import datetime


class AppSettings(db.Model):
    """Application settings stored in database"""
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.UUID(as_uuid=True), db.ForeignKey('admin_users.id'))
    
    def __repr__(self):
        return f'<AppSettings {self.key}={self.value}>'
    
    @staticmethod
    def get(key, default=None):
        """Get a setting value by key"""
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            # Try to parse boolean values
            if setting.value.lower() in ['true', 'false']:
                return setting.value.lower() == 'true'
            return setting.value
        return default
    
    @staticmethod
    def set(key, value, description=None, updated_by=None):
        """Set a setting value"""
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
            setting.updated_by = updated_by
        else:
            setting = AppSettings(
                key=key,
                value=str(value),
                description=description,
                updated_by=updated_by
            )
            db.session.add(setting)
        db.session.commit()
        return setting
    
    @staticmethod
    def get_all():
        """Get all settings as a dictionary"""
        settings = AppSettings.query.all()
        return {s.key: s.value for s in settings}
