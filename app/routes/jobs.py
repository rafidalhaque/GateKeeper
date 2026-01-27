"""
Background job monitoring API endpoints
"""
from flask import Blueprint, jsonify, request
from app.models import db
from app.models.events import CeleryJob
from app.utils.auth import admin_required
from sqlalchemy import desc

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')


@bp.route('/', methods=['GET'])
@admin_required
def list_jobs():
    """Get list of background jobs"""
    status_filter = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)

    query = CeleryJob.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    jobs = query.order_by(desc(CeleryJob.created_at)).limit(limit).all()

    return jsonify([{
        'id': str(job.id),
        'task_name': job.task_name,
        'task_id': job.task_id,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    } for job in jobs])


@bp.route('/<string:task_id>', methods=['GET'])
@admin_required
def get_job_status(task_id):
    """Get status of a specific job"""
    job = CeleryJob.query.filter_by(task_id=task_id).first_or_404()

    return jsonify({
        'id': str(job.id),
        'task_name': job.task_name,
        'task_id': job.task_id,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'error_message': job.error_message,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    })


@bp.route('/active', methods=['GET'])
@admin_required
def get_active_jobs():
    """Get all active (queued or processing) jobs"""
    jobs = CeleryJob.query.filter(
        CeleryJob.status.in_(['queued', 'processing'])
    ).order_by(desc(CeleryJob.created_at)).all()

    return jsonify([{
        'id': str(job.id),
        'task_name': job.task_name,
        'task_id': job.task_id,
        'status': job.status,
        'progress': job.progress,
        'total_items': job.total_items,
        'processed_items': job.processed_items,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
    } for job in jobs])


@bp.route('/stats', methods=['GET'])
@admin_required
def get_job_stats():
    """Get job statistics"""
    total = CeleryJob.query.count()
    queued = CeleryJob.query.filter_by(status='queued').count()
    processing = CeleryJob.query.filter_by(status='processing').count()
    completed = CeleryJob.query.filter_by(status='completed').count()
    failed = CeleryJob.query.filter_by(status='failed').count()

    return jsonify({
        'total': total,
        'queued': queued,
        'processing': processing,
        'completed': completed,
        'failed': failed,
        'active': queued + processing
    })


@bp.route('/<string:task_id>', methods=['DELETE'])
@admin_required
def delete_job(task_id):
    """Delete a job record"""
    job = CeleryJob.query.filter_by(task_id=task_id).first_or_404()

    # Only allow deletion of completed or failed jobs
    if job.status in ['queued', 'processing']:
        return jsonify({'error': 'Cannot delete active jobs'}), 400

    db.session.delete(job)
    db.session.commit()

    return jsonify({'message': 'Job deleted successfully'})


@bp.route('/clear-completed', methods=['POST'])
@admin_required
def clear_completed_jobs():
    """Clear all completed jobs"""
    deleted_count = CeleryJob.query.filter_by(status='completed').delete()
    db.session.commit()

    return jsonify({
        'message': 'Completed jobs cleared',
        'deleted_count': deleted_count
    })
