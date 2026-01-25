"""
Role-Based Access Control (RBAC) models
"""
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.models import db


class Role(db.Model):
    """Role model"""
    __tablename__ = 'roles'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), unique=True, nullable=False)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_users = relationship('AdminUser', back_populates='role')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class Permission(db.Model):
    """Permission model - system-reserved, auto-generated"""
    __tablename__ = 'permissions'
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    key = db.Column(String(100), unique=True, nullable=False)  # e.g., 'participant.read'
    description = db.Column(Text)
    feature_group = db.Column(String(100))  # e.g., 'participants', 'teams', 'attendance'
    system_reserved = db.Column(Boolean, default=True)  # always true, non-deletable
    
    # Relationships
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')
    
    def __repr__(self):
        return f'<Permission {self.key}>'


class RolePermission(db.Model):
    """Many-to-many relationship between roles and permissions"""
    __tablename__ = 'role_permissions'
    
    role_id = db.Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = db.Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)


class AdminUser(db.Model):
    """Admin user model"""
    __tablename__ = 'admin_users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_user_id = db.Column(String(255), unique=True, nullable=True)
    role_id = db.Column(Integer, ForeignKey('roles.id', ondelete='SET NULL'))
    email = db.Column(String(255), unique=True, nullable=False)
    name = db.Column(String(255))
    is_super_admin = db.Column(Boolean, default=False)  # Super admin bypass
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role = relationship('Role', back_populates='admin_users')
    checkin_logs = relationship('CheckinLog', back_populates='admin_user')
    
    def __repr__(self):
        return f'<AdminUser {self.email}>'
    
    def has_permission(self, permission_key):
        """Check if user has a specific permission"""
        if self.is_super_admin:
            return True
        
        if not self.role:
            return False
        
        return any(p.key == permission_key for p in self.role.permissions)
    
    def has_any_permission(self, permission_keys):
        """Check if user has any of the specified permissions"""
        if self.is_super_admin:
            return True
        
        if not self.role:
            return False
        
        return any(p.key in permission_keys for p in self.role.permissions)


class SMTPConfig(db.Model):
    """SMTP Configuration - stored in database, supersedes .env"""
    __tablename__ = 'smtp_config'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    smtp_server = db.Column(String(255), nullable=False)
    smtp_port = db.Column(Integer, nullable=False, default=587)
    smtp_username = db.Column(String(255), nullable=False)
    smtp_password = db.Column(String(255), nullable=False)  # Should be encrypted in production
    smtp_use_tls = db.Column(Boolean, default=True)
    smtp_use_ssl = db.Column(Boolean, default=False)
    sender_email = db.Column(String(255), nullable=False)
    sender_name = db.Column(String(255), default='GateKeeper')
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(UUID(as_uuid=True), ForeignKey('admin_users.id'))

    def __repr__(self):
        return f'<SMTPConfig {self.smtp_server}:{self.smtp_port}>'


class PendingInvitation(db.Model):
    """Pending admin user invitations"""
    __tablename__ = 'pending_invitations'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(String(255), unique=True, nullable=False)
    name = db.Column(String(255))
    role_id = db.Column(Integer, ForeignKey('roles.id'))
    invited_by = db.Column(UUID(as_uuid=True), ForeignKey('admin_users.id'))
    invitation_token = db.Column(String(255), unique=True, nullable=False)
    supabase_user_id = db.Column(String(255), unique=True, nullable=True)  # Set when user is created in Supabase
    expires_at = db.Column(DateTime, nullable=False)
    accepted_at = db.Column(DateTime, nullable=True)
    status = db.Column(String(50), default='pending')  # pending, accepted, expired
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship('Role')
    inviter = relationship('AdminUser', foreign_keys=[invited_by])

    def __repr__(self):
        return f'<PendingInvitation {self.email}>'


# Import CheckinLog after all classes are defined to avoid circular import issues
# This ensures SQLAlchemy can resolve the 'CheckinLog' relationship in AdminUser
from app.models.events import CheckinLog  # noqa: F401, E402
