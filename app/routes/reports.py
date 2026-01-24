"""
Reports and analytics routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import Event, Participant, Team, CheckinLog
from app.utils.auth import permission_required
from sqlalchemy import func

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/attendance-summary', methods=['GET'])
@permission_required('report.read')
def attendance_summary():
    """Get attendance summary for an event"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    event = Event.query.get_or_404(event_id)
    
    # Get counts
    total_registered = Participant.query.filter_by(event_id=event_id).count()
    total_attended = Participant.query.filter_by(event_id=event_id, attendance_status=True).count()
    
    attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0
    
    response = {
        'event_id': str(event_id),
        'event_name': event.name,
        'total_registered': total_registered,
        'total_attended': total_attended,
        'no_show': total_registered - total_attended,
        'attendance_rate': round(attendance_rate, 2)
    }
    
    # Add team stats if team mode
    if event.mode == 'team':
        total_teams = Team.query.filter_by(event_id=event_id).count()
        empty_teams = Team.query.filter_by(event_id=event_id, is_empty=True).count()
        
        response['total_teams'] = total_teams
        response['empty_teams'] = empty_teams
    
    return jsonify(response)


@bp.route('/export-csv', methods=['GET'])
@permission_required('report.export')
def export_csv():
    """Export participants data as CSV"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    # TODO: Implement CSV export
    
    return jsonify({
        'message': 'CSV export',
        'event_id': event_id
    })


@bp.route('/team-stats', methods=['GET'])
@permission_required('report.read')
def team_stats():
    """Get team-wise statistics"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    event = Event.query.get_or_404(event_id)
    
    if event.mode != 'team':
        return jsonify({'error': 'Event is not in team mode'}), 400
    
    # Get team stats
    teams = Team.query.filter_by(event_id=event_id).all()
    
    stats = []
    for team in teams:
        total_members = len(team.participants)
        attended_members = sum(1 for p in team.participants if p.attendance_status)
        attendance_rate = (attended_members / total_members * 100) if total_members > 0 else 0
        
        stats.append({
            'team_id': team.id,
            'team_name': team.team_name,
            'total_members': total_members,
            'attended_members': attended_members,
            'attendance_rate': round(attendance_rate, 2),
            'is_empty': team.is_empty
        })
    
    return jsonify(stats)


@bp.route('/checkin-timeline', methods=['GET'])
@permission_required('report.read')
def checkin_timeline():
    """Get check-in timeline data"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    # Get check-ins grouped by hour
    checkins = CheckinLog.query.filter_by(event_id=event_id).all()
    
    # Group by hour
    timeline = {}
    for checkin in checkins:
        hour = checkin.checked_in_at.strftime('%Y-%m-%d %H:00')
        timeline[hour] = timeline.get(hour, 0) + 1
    
    return jsonify({
        'event_id': event_id,
        'timeline': [{'hour': k, 'count': v} for k, v in sorted(timeline.items())]
    })
