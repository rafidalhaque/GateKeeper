"""
Ticket generation and download routes
"""
from flask import Blueprint, request, jsonify, send_file
from app.models import db
from app.models.events import Event, Participant, CeleryJob
from app.utils.auth import permission_required
from app.services.tasks import generate_tickets_task
from app.services.ticket_service import generate_ticket_pdf
import io

bp = Blueprint('tickets', __name__, url_prefix='/api/tickets')


@bp.route('/generate', methods=['POST'])
@permission_required('ticket.generate')
def generate_tickets():
    """Queue ticket generation job"""
    data = request.get_json()
    
    if 'event_id' not in data:
        return jsonify({'error': 'Missing event_id'}), 400
    
    # Validate event exists
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Queue background job
    task = generate_tickets_task.delay(data['event_id'])
    
    return jsonify({
        'message': 'Ticket generation queued',
        'job_id': task.id,
        'status': 'queued'
    }), 202


@bp.route('/status/<job_id>', methods=['GET'])
@permission_required('ticket.read')
def get_ticket_generation_status(job_id):
    """Get ticket generation job status"""
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


@bp.route('/download/<uuid:unique_uuid>', methods=['GET'])
def download_ticket(unique_uuid):
    """Download ticket PDF (public endpoint)"""
    participant = Participant.query.filter_by(unique_url_uuid=unique_uuid).first_or_404()
    
    # Generate PDF
    pdf = generate_ticket_pdf(participant.id)
    
    if not pdf:
        return jsonify({'error': 'Failed to generate ticket'}), 500
    
    # Send PDF as response
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'ticket_{participant.name.replace(" ", "_")}.pdf'
    )
