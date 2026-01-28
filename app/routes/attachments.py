"""
Image Attachment Routes for Template Designer
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app.models import db
from app.models.attachments import ImageAttachment
from app.utils.auth import permission_required
import os
import uuid
from pathlib import Path
import mimetypes

bp = Blueprint('attachments', __name__, url_prefix='/api/attachments')

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_directory():
    """Get the upload directory path"""
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    attachments_dir = Path(upload_folder) / 'attachments'

    # If it's a relative path, make it relative to the project root
    if not attachments_dir.is_absolute():
        attachments_dir = Path(current_app.root_path).parent / attachments_dir

    attachments_dir.mkdir(parents=True, exist_ok=True)
    return attachments_dir

@bp.route('/upload', methods=['POST'])
@permission_required('manage_email_templates')
def upload_image():
    """Upload an image attachment"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400

        # Get additional metadata
        description = request.form.get('description', '')
        usage_type = request.form.get('usage_type', 'all')
        
        if usage_type not in ['email', 'ticket', 'token', 'all']:
            usage_type = 'all'

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Generate unique CID
        cid = f"img_{uuid.uuid4().hex}@gatekeeper"

        # Save file
        upload_dir = get_upload_directory()
        file_path = upload_dir / unique_filename
        file.save(str(file_path))

        # Get content type
        content_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'

        # Get current user
        from flask import g
        user_id = g.current_user.id if hasattr(g, 'current_user') and g.current_user else None

        # Store relative path (uploads/attachments/filename.ext)
        relative_path = f"uploads/attachments/{unique_filename}"

        # Create database record
        attachment = ImageAttachment(
            filename=unique_filename,
            original_filename=original_filename,
            content_type=content_type,
            file_size=file_size,
            file_path=relative_path,
            cid=cid,
            description=description,
            uploaded_by=user_id,
            usage_type=usage_type
        )

        db.session.add(attachment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'attachment': attachment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()

        # Cleanup: delete uploaded file if database insert failed
        try:
            if 'file_path' in locals() and Path(file_path).exists():
                Path(file_path).unlink()
                current_app.logger.info(f"Cleaned up uploaded file after error: {file_path}")
        except Exception as cleanup_error:
            current_app.logger.error(f"Failed to cleanup file: {cleanup_error}")

        current_app.logger.error(f"Error uploading image: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@permission_required('manage_email_templates')
def list_attachments():
    """List all image attachments"""
    try:
        usage_type = request.args.get('usage_type')
        
        query = ImageAttachment.query.filter_by(is_active=True)
        
        if usage_type and usage_type in ['email', 'ticket', 'token']:
            query = query.filter(
                (ImageAttachment.usage_type == usage_type) | 
                (ImageAttachment.usage_type == 'all')
            )
        
        attachments = query.order_by(ImageAttachment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'attachments': [att.to_dict() for att in attachments]
        })

    except Exception as e:
        current_app.logger.error(f"Error listing attachments: {str(e)}")
        return jsonify({'error': f'Failed to list attachments: {str(e)}'}), 500

@bp.route('/<attachment_id>', methods=['GET'])
def get_attachment_details(attachment_id):
    """Get attachment details"""
    try:
        attachment = ImageAttachment.query.filter_by(id=attachment_id, is_active=True).first()
        
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404
        
        return jsonify({
            'success': True,
            'attachment': attachment.to_dict()
        })

    except Exception as e:
        current_app.logger.error(f"Error getting attachment: {str(e)}")
        return jsonify({'error': f'Failed to get attachment: {str(e)}'}), 500

@bp.route('/image/<attachment_id>', methods=['GET'])
def serve_image(attachment_id):
    """Serve the image file"""
    try:
        attachment = ImageAttachment.query.filter_by(id=attachment_id, is_active=True).first()
        
        if not attachment:
            return jsonify({'error': 'Image not found'}), 404

        # Construct full file path
        # attachment.file_path is like "uploads/attachments/uuid.jpg"
        project_root = Path(current_app.root_path).parent
        file_path = project_root / attachment.file_path

        if not file_path.exists():
            current_app.logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'Image file not found on server'}), 404

        return send_file(
            str(file_path),
            mimetype=attachment.content_type,
            as_attachment=False,
            download_name=attachment.original_filename
        )

    except Exception as e:
        current_app.logger.error(f"Error serving image: {str(e)}")
        return jsonify({'error': f'Failed to serve image: {str(e)}'}), 500

@bp.route('/<attachment_id>', methods=['PUT'])
@permission_required('manage_email_templates')
def update_attachment(attachment_id):
    """Update attachment metadata"""
    try:
        attachment = ImageAttachment.query.filter_by(id=attachment_id, is_active=True).first()
        
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        data = request.get_json()
        
        if 'description' in data:
            attachment.description = data['description']
        
        if 'usage_type' in data and data['usage_type'] in ['email', 'ticket', 'token', 'all']:
            attachment.usage_type = data['usage_type']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Attachment updated successfully',
            'attachment': attachment.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating attachment: {str(e)}")
        return jsonify({'error': f'Failed to update attachment: {str(e)}'}), 500

@bp.route('/<attachment_id>', methods=['DELETE'])
@permission_required('manage_email_templates')
def delete_attachment(attachment_id):
    """Delete an attachment (soft delete)"""
    try:
        attachment = ImageAttachment.query.filter_by(id=attachment_id, is_active=True).first()
        
        if not attachment:
            return jsonify({'error': 'Attachment not found'}), 404

        # Soft delete
        attachment.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Attachment deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting attachment: {str(e)}")
        return jsonify({'error': f'Failed to delete attachment: {str(e)}'}), 500
