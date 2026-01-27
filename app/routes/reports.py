"""
Reports and analytics routes
"""
from flask import Blueprint, request, jsonify, make_response
from app.models import db
from app.models.events import Event, Participant, Team, CheckinLog
from app.utils.auth import permission_required
from sqlalchemy import func
from datetime import datetime
import csv
import io

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/event/<uuid:event_id>', methods=['GET'])
@permission_required('report.read')
def get_event_report(event_id):
    """Get comprehensive report for a specific event"""
    event = Event.query.get_or_404(event_id)

    # Get participant statistics
    total_participants = Participant.query.filter_by(event_id=event_id).count()
    checked_in_count = Participant.query.filter_by(event_id=event_id, attendance_status=True).count()

    attendance_rate = (checked_in_count / total_participants * 100) if total_participants > 0 else 0

    report_data = {
        'event_id': str(event_id),
        'event_name': event.name,
        'event_date': event.date.isoformat() if event.date else None,
        'event_venue': event.venue,
        'event_mode': event.mode,
        'total_participants': total_participants,
        'checked_in': checked_in_count,
        'not_checked_in': total_participants - checked_in_count,
        'attendance_rate': round(attendance_rate, 2),
        'team_stats': [],
        'recent_checkins': []
    }

    # Add team statistics if event is in team mode
    if event.mode == 'team':
        teams = Team.query.filter_by(event_id=event_id).all()
        report_data['total_teams'] = len(teams)

        team_stats = []
        for team in teams:
            participants = Participant.query.filter_by(event_id=event_id, team_id=team.id).all()
            member_count = len(participants)
            checked_in = sum(1 for p in participants if p.attendance_status)
            team_attendance = (checked_in / member_count * 100) if member_count > 0 else 0

            team_stats.append({
                'id': team.id,
                'team_name': team.team_name,
                'member_count': member_count,
                'checked_in': checked_in,
                'attendance_rate': round(team_attendance, 2)
            })

        report_data['team_stats'] = team_stats

    # Get recent check-ins (last 50)
    recent_checkins = (CheckinLog.query
                      .filter_by(event_id=event_id)
                      .order_by(CheckinLog.checked_in_at.desc())
                      .limit(50)
                      .all())

    recent_checkins_data = []
    for checkin in recent_checkins:
        participant = Participant.query.get(checkin.participant_id)
        if participant:
            checkin_data = {
                'id': checkin.id,
                'participant_name': participant.name,
                'participant_email': participant.email,
                'checked_in_at': checkin.checked_in_at.isoformat()
            }

            if event.mode == 'team' and participant.team_id:
                team = Team.query.get(participant.team_id)
                checkin_data['team_name'] = team.team_name if team else 'N/A'
            else:
                checkin_data['team_name'] = 'N/A'

            recent_checkins_data.append(checkin_data)

    report_data['recent_checkins'] = recent_checkins_data

    return jsonify(report_data)


@bp.route('/event/<uuid:event_id>/export', methods=['GET'])
@permission_required('report.export')
def export_event_report(event_id):
    """Export event report as CSV"""
    event = Event.query.get_or_404(event_id)

    # Get all participants with their check-in status
    participants = (Participant.query
                   .filter_by(event_id=event_id)
                   .order_by(Participant.participant_name)
                   .all())

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    headers = ['Name', 'Email', 'Attendance Status', 'Check-in Time']
    if event.mode == 'team':
        headers.insert(2, 'Team')

    # Add custom fields to headers if they exist
    if event.custom_fields:
        for field in event.custom_fields:
            headers.append(field.get('label', field.get('name', 'Unknown')))

    writer.writerow(headers)

    # Write participant data
    for participant in participants:
        row = [
            participant.name,
            participant.email,
        ]

        # Add team if in team mode
        if event.mode == 'team':
            team_name = 'N/A'
            if participant.team_id:
                team = Team.query.get(participant.team_id)
                team_name = team.team_name if team else 'N/A'
            row.append(team_name)

        # Add attendance status
        row.append('Checked In' if participant.attendance_status else 'Not Checked In')

        # Add check-in time
        if participant.attendance_status:
            checkin = CheckinLog.query.filter_by(
                event_id=event_id,
                participant_id=participant.id
            ).order_by(CheckinLog.checked_in_at.desc()).first()

            if checkin:
                row.append(checkin.checked_in_at.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row.append('N/A')
        else:
            row.append('N/A')

        # Add custom fields data
        if event.custom_fields and participant.custom_data:
            for field in event.custom_fields:
                field_name = field.get('name', '')
                value = participant.custom_data.get(field_name, 'N/A')
                row.append(value)
        elif event.custom_fields:
            for _ in event.custom_fields:
                row.append('N/A')

        writer.writerow(row)

    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=report_{event.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return response

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
