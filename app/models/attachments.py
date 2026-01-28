"""
Image Attachment Model for Email Templates, Tickets, and Tokens
"""
from app.models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class ImageAttachment(db.Model):
    """Model for storing uploaded images used in templates"""
    __tablename__ = 'image_attachments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    file_path = db.Column(db.String(500), nullable=False)  # Path relative to upload directory
    cid = db.Column(db.String(100), unique=True, nullable=False)  # Content-ID for email embedding
    description = db.Column(db.Text)
    uploaded_by = db.Column(UUID(as_uuid=True), db.ForeignKey('admin_users.id'), nullable=False)
    usage_type = db.Column(db.String(50), nullable=False)  # 'email', 'ticket', 'token', 'all'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    uploader = db.relationship('AdminUser', backref='uploaded_images', foreign_keys=[uploaded_by])

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'cid': self.cid,
            'description': self.description,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.name if self.uploader else None,
            'usage_type': self.usage_type,
            'is_active': self.is_active,
            'url': f'/api/attachments/image/{self.id}',
            'html_img_tag': f'<img src="cid:{self.cid}" alt="{self.description or self.original_filename}" />',
            'html_data_uri': f'/api/attachments/image/{self.id}',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<ImageAttachment {self.filename}>'
