"""
Email template management routes
"""
from flask import Blueprint, jsonify, request, render_template
from app.models import db
from app.models.events import EmailTemplate
from app.utils.auth import admin_required, permission_required
from datetime import datetime
import uuid

bp = Blueprint('email_templates', __name__)


@bp.route('/admin/email-templates')
@admin_required
def email_templates_page():
    """Render email templates management page"""
    return render_template('admin/email_templates.html')


@bp.route('/api/email-templates', methods=['GET'])
@permission_required('email_template.read')
def list_templates():
    """Get all email templates"""
    try:
        templates = EmailTemplate.query.order_by(EmailTemplate.updated_at.desc()).all()

        return jsonify([{
            'id': str(t.id),
            'name': t.name,
            'type': t.type,
            'subject': t.subject,
            'description': t.description,
            'html_content': t.html_content,
            'text_content': t.text_content,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'updated_at': t.updated_at.isoformat() if t.updated_at else None
        } for t in templates]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/email-templates/<template_id>', methods=['GET'])
@permission_required('email_template.read')
def get_template(template_id):
    """Get single email template"""
    try:
        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        return jsonify({
            'id': str(template.id),
            'name': template.name,
            'type': template.type,
            'subject': template.subject,
            'description': template.description,
            'html_content': template.html_content,
            'text_content': template.text_content,
            'created_at': template.created_at.isoformat() if template.created_at else None,
            'updated_at': template.updated_at.isoformat() if template.updated_at else None
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/email-templates', methods=['POST'])
@permission_required('email_template.create')
def create_template():
    """Create new email template"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name') or not data.get('subject'):
            return jsonify({'error': 'Name and subject are required'}), 400

        template = EmailTemplate(
            id=uuid.uuid4(),
            name=data['name'],
            type=data.get('type', 'custom'),
            subject=data['subject'],
            description=data.get('description'),
            html_content=data.get('html_content', ''),
            text_content=data.get('text_content', ''),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(template)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Template created successfully',
            'template': {
                'id': str(template.id),
                'name': template.name,
                'type': template.type
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/email-templates/<template_id>', methods=['PUT'])
@permission_required('email_template.update')
def update_template(template_id):
    """Update email template"""
    try:
        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        data = request.get_json()

        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'type' in data:
            template.type = data['type']
        if 'subject' in data:
            template.subject = data['subject']
        if 'description' in data:
            template.description = data['description']
        if 'html_content' in data:
            template.html_content = data['html_content']
        if 'text_content' in data:
            template.text_content = data['text_content']

        template.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Template updated successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/email-templates/<template_id>', methods=['DELETE'])
@permission_required('email_template.delete')
def delete_template(template_id):
    """Delete email template"""
    try:
        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        db.session.delete(template)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Template deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/api/email-templates/send-test', methods=['POST'])
@permission_required('email_template.test')
def send_test_email():
    """Send test email using template"""
    try:
        from app.services.email_service import send_email
        from jinja2 import Template

        data = request.get_json()
        template_id = data.get('template_id')
        recipient_email = data.get('email')

        if not template_id or not recipient_email:
            return jsonify({'error': 'Template ID and email are required'}), 400

        template = EmailTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        # Sample data for testing
        sample_data = {
            'participant': {
                'name': 'John Doe',
                'email': recipient_email,
                'unique_url': 'http://localhost:5000/ticket/sample-uuid',
                'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
            },
            'event': {
                'name': 'Tech Conference 2026',
                'date': 'January 25, 2026',
                'venue': 'Convention Center',
                'mode': 'solo'
            },
            'team': {
                'name': 'Team Alpha',
                'id': '1'
            },
            'current_year': datetime.utcnow().year,
            'app_name': 'GateKeeper'
        }

        # Render template with sample data
        subject_template = Template(template.subject)
        subject = subject_template.render(**sample_data)

        html_template = Template(template.html_content)
        html_content = html_template.render(**sample_data)

        text_template = Template(template.text_content) if template.text_content else None
        text_content = text_template.render(**sample_data) if text_template else None

        # Send email
        success, error = send_email(
            recipient=recipient_email,
            subject=f"[TEST] {subject}",
            body=text_content or 'Test email',
            html=html_content
        )

        if success:
            return jsonify({
                'success': True,
                'message': 'Test email sent successfully'
            }), 200
        else:
            return jsonify({
                'error': f'Failed to send test email: {error}'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
