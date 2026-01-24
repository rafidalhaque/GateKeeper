"""
Email sending and management routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import EmailLog, Event, Participant, CeleryJob
from app.utils.auth import permission_required
from app.services.tasks import send_bulk_emails_task
from app.services.email_service import retry_failed_emails

bp = Blueprint('emails', __name__, url_prefix='/api/email')


@bp.route('/send-bulk', methods=['POST'])
@permission_required('email.send_bulk')
def send_bulk_emails():
    """Queue bulk email sending job"""
    data = request.get_json()
    
    required_fields = ['event_id', 'subject', 'template_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate event exists
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Get recipients (all participants for the event)
    participants = Participant.query.filter_by(event_id=data['event_id']).all()
    
    recipients = [{
        'email': p.email,
        'name': p.name,
        'unique_url_uuid': str(p.unique_url_uuid)
    } for p in participants]
    
    # Queue background job
    task = send_bulk_emails_task.delay(
        data['event_id'],
        data['subject'],
        data['template_name'],
        recipients
    )
    
    return jsonify({
        'message': 'Bulk email job queued',
        'job_id': task.id,
        'status': 'queued',
        'recipient_count': len(recipients)
    }), 202


@bp.route('/status/<job_id>', methods=['GET'])
@permission_required('email.read_logs')
def get_email_job_status(job_id):
    """Get email sending job status"""
    job = CeleryJob.query.filter_by(task_id=job_id).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job.task_id,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'error_message': job.error_message
    })


@bp.route('/retry-failed', methods=['POST'])
@permission_required('email.send_bulk')
def retry_failed():
    """Retry failed email deliveries"""
    data = request.get_json()
    event_id = data.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id'}), 400
    
    # Retry failed emails
    result = retry_failed_emails(event_id)
    
    return jsonify(result), 200


@bp.route('/logs', methods=['GET'])
@permission_required('email.read_logs')
def get_email_logs():
    """Get email logs for an event"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    logs = EmailLog.query.filter_by(event_id=event_id).order_by(EmailLog.created_at.desc()).all()
    
    return jsonify([{
        'id': log.id,
        'recipient_email': log.recipient_email,
        'subject': log.subject,
        'status': log.status,
        'error_message': log.error_message,
        'retry_count': log.retry_count,
        'created_at': log.created_at.isoformat(),
        'sent_at': log.sent_at.isoformat() if log.sent_at else None
    } for log in logs])
