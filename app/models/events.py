"""
Core database models for GateKeeper event management system
"""
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Text, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models import db


class Event(db.Model):
    """Event model"""
    __tablename__ = 'events'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(String(255), nullable=False)
    date = db.Column(DateTime, nullable=False)
    venue = db.Column(String(500))
    mode = db.Column(String(20), nullable=False)  # 'solo' or 'team'
    passcode = db.Column(String(100))  # nullable, for fallback/public access
    ticket_template_html = db.Column(Text)
    ticket_template_css = db.Column(Text)
    custom_fields = db.Column(JSONB)  # flexible field configuration
    schedule_config = db.Column(JSONB)  # prayer times, breaks, session timings
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teams = relationship('Team', back_populates='event', cascade='all, delete-orphan')
    participants = relationship('Participant', back_populates='event', cascade='all, delete-orphan')
    email_logs = relationship('EmailLog', back_populates='event', cascade='all, delete-orphan')
    checkin_logs = relationship('CheckinLog', back_populates='event', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Event {self.name}>'


class Team(db.Model):
    """Team model for team-based events"""
    __tablename__ = 'teams'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    event_id = db.Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    team_name = db.Column(String(255), nullable=False)
    is_empty = db.Column(Boolean, default=False)  # auto-updated when last member is removed
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship('Event', back_populates='teams')
    participants = relationship('Participant', back_populates='team')
    
    def __repr__(self):
        return f'<Team {self.team_name}>'


class Participant(db.Model):
    """Participant model"""
    __tablename__ = 'participants'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = db.Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'))
    name = db.Column(String(255), nullable=False)
    email = db.Column(String(255), nullable=False)
    t_shirt_size = db.Column(String(10))
    custom_data = db.Column(JSONB)  # stores event-specific custom field values
    unique_url_uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    attendance_status = db.Column(Boolean, default=False)
    attended_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    event = relationship('Event', back_populates='participants')
    team = relationship('Team', back_populates='participants')
    checkin_logs = relationship('CheckinLog', back_populates='participant', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Participant {self.name}>'


class EmailLog(db.Model):
    """Email log for tracking email delivery"""
    __tablename__ = 'email_logs'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    recipient_email = db.Column(String(255), nullable=False)
    subject = db.Column(String(500))
    template_name = db.Column(String(100))
    status = db.Column(String(20), default='queued')  # 'queued', 'sent', 'failed'
    error_message = db.Column(Text)
    retry_count = db.Column(Integer, default=0)
    next_retry_at = db.Column(DateTime)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    sent_at = db.Column(DateTime)
    
    # Relationships
    event = relationship('Event', back_populates='email_logs')
    
    def __repr__(self):
        return f'<EmailLog {self.recipient_email} - {self.status}>'


class CheckinLog(db.Model):
    """Check-in log for audit trail"""
    __tablename__ = 'checkin_logs'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    participant_id = db.Column(UUID(as_uuid=True), ForeignKey('participants.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    checked_in_by = db.Column(UUID(as_uuid=True), ForeignKey('admin_users.id', ondelete='SET NULL'))
    ip_address = db.Column(String(45))
    user_agent = db.Column(Text)
    device_fingerprint = db.Column(String(255))
    checked_in_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    participant = relationship('Participant', back_populates='checkin_logs')
    event = relationship('Event', back_populates='checkin_logs')
    admin_user = relationship('AdminUser', back_populates='checkin_logs')
    
    def __repr__(self):
        return f'<CheckinLog {self.participant_id} at {self.checked_in_at}>'


class CeleryJob(db.Model):
    """Celery job tracking"""
    __tablename__ = 'celery_jobs'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_name = db.Column(String(255), nullable=False)
    task_id = db.Column(String(255), unique=True, nullable=False)
    status = db.Column(String(20), default='queued')  # 'queued', 'processing', 'completed', 'failed'
    progress = db.Column(Integer, default=0)  # 0-100
    total_items = db.Column(Integer)
    processed_items = db.Column(Integer, default=0)
    error_message = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    started_at = db.Column(DateTime)
    completed_at = db.Column(DateTime)
    
    def __repr__(self):
        return f'<CeleryJob {self.task_name} - {self.status}>'


# Import AdminUser after all classes are defined to avoid circular import issues
# This ensures SQLAlchemy can resolve the 'AdminUser' relationship in CheckinLog
from app.models.auth import AdminUser  # noqa: F401, E402


class EmailTemplate(db.Model):
    """Email template model for managing email designs"""
    __tablename__ = 'email_templates'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(String(255), nullable=False)
    type = db.Column(String(50), nullable=False)  # 'ticket', 'announcement', 'reminder', 'custom'
    subject = db.Column(String(500), nullable=False)
    description = db.Column(Text)
    html_content = db.Column(Text, nullable=False)
    text_content = db.Column(Text)  # plain text fallback
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

