"""
CSV import routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import Event
from app.utils.auth import permission_required
from app.services.tasks import import_csv_task

bp = Blueprint('csv', __name__, url_prefix='/api/import')


@bp.route('/csv', methods=['POST'])
@permission_required('csv.import')
def import_csv():
    """Import participants from CSV file"""
    # Get event_id from form data
    event_id = request.form.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id'}), 400
    
    # Validate event exists
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Get CSV file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be CSV format'}), 400
    
    # Read CSV content
    try:
        csv_content = file.read().decode('utf-8')
    except Exception as e:
        return jsonify({'error': f'Failed to read CSV file: {str(e)}'}), 400
    
    # Queue background job
    task = import_csv_task.delay(event_id, csv_content)
    
    return jsonify({
        'message': 'CSV import job queued',
        'job_id': task.id,
        'status': 'queued'
    }), 202


@bp.route('/status/<job_id>', methods=['GET'])
@permission_required('csv.import')
def get_import_status(job_id):
    """Get CSV import job status"""
    from app.models.events import CeleryJob
    
    job = CeleryJob.query.filter_by(task_id=job_id).first()
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job.task_id,
        'task_name': job.task_name,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat(),
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    })
