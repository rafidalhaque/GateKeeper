"""
Dashboard statistics routes
"""
from flask import Blueprint, jsonify
from app.models import db
from app.models.events import Event, Participant, CheckinLog
from app.utils.auth import permission_required
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@bp.route('/dashboard', methods=['GET'])
@permission_required('dashboard.view')
def get_dashboard_stats():
    """Get dashboard statistics"""

    # Total events
    total_events = Event.query.count()

    # Total participants
    total_participants = Participant.query.count()

    # Total check-ins (all time)
    total_checkins = Participant.query.filter_by(attendance_status=True).count()

    # Check-ins per event
    checkins_per_event = db.session.query(
        Event.id,
        Event.name,
        func.count(Participant.id).filter(Participant.attendance_status == True).label('checkins'),
        func.count(Participant.id).label('total_participants')
    ).outerjoin(Participant, Event.id == Participant.event_id)\
     .group_by(Event.id, Event.name)\
     .all()

    # Format check-ins per event
    event_checkins = []
    for event_id, event_name, checkins, total in checkins_per_event:
        event_checkins.append({
            'event_id': str(event_id),
            'event_name': event_name,
            'checkins': checkins or 0,
            'total_participants': total or 0,
            'checkin_percentage': round((checkins / total * 100) if total > 0 else 0, 1)
        })

    # Active events (today)
    today = datetime.utcnow().date()
    active_events = Event.query.filter(
        func.date(Event.date) == today
    ).count()

    # Check-ins today
    yesterday = datetime.utcnow() - timedelta(days=1)
    checkins_today = Participant.query.filter(
        Participant.attendance_status == True,
        Participant.attended_at >= yesterday
    ).count()

    # Upcoming events
    upcoming_events = Event.query.filter(
        Event.date >= datetime.utcnow()
    ).order_by(Event.date.asc()).limit(5).all()

    upcoming_events_data = [{
        'id': str(event.id),
        'name': event.name,
        'date': event.date.isoformat(),
        'venue': event.venue,
        'mode': event.mode,
        'participant_count': Participant.query.filter_by(event_id=event.id).count()
    } for event in upcoming_events]

    # Recent activity (last 10 check-ins)
    recent_checkins = CheckinLog.query.order_by(
        CheckinLog.checked_in_at.desc()
    ).limit(10).all()

    recent_activity = []
    for log in recent_checkins:
        participant = Participant.query.get(log.participant_id)
        event = Event.query.get(log.event_id)
        if participant and event:
            time_diff = datetime.utcnow() - log.checked_in_at
            if time_diff.seconds < 60:
                time_str = 'Just now'
            elif time_diff.seconds < 3600:
                time_str = f'{time_diff.seconds // 60} minutes ago'
            elif time_diff.days == 0:
                time_str = f'{time_diff.seconds // 3600} hours ago'
            else:
                time_str = f'{time_diff.days} days ago'

            recent_activity.append({
                'id': log.id,
                'description': f'{participant.name} checked in to {event.name}',
                'time': time_str,
                'checked_in_at': log.checked_in_at.isoformat()
            })

    return jsonify({
        'stats': {
            'total_events': total_events,
            'total_participants': total_participants,
            'total_checkins': total_checkins,
            'active_events': active_events,
            'checkins_today': checkins_today
        },
        'checkins_per_event': event_checkins,
        'upcoming_events': upcoming_events_data,
        'recent_activity': recent_activity
    })


@bp.route('/event/<uuid:event_id>', methods=['GET'])
@permission_required('dashboard.view')
def get_event_stats(event_id):
    """Get statistics for a specific event"""

    event = Event.query.get_or_404(event_id)

    # Total participants
    total_participants = Participant.query.filter_by(event_id=event_id).count()

    # Checked in participants
    checked_in = Participant.query.filter_by(
        event_id=event_id,
        attendance_status=True
    ).count()

    # Not checked in
    not_checked_in = total_participants - checked_in

    # Check-in percentage
    checkin_percentage = round((checked_in / total_participants * 100) if total_participants > 0 else 0, 1)

    # Teams stats (if team mode)
    teams_stats = []
    if event.mode == 'team':
        from app.models.events import Team
        teams = Team.query.filter_by(event_id=event_id).all()

        for team in teams:
            team_participants = Participant.query.filter_by(team_id=team.id).all()
            team_checked_in = sum(1 for p in team_participants if p.attendance_status)

            teams_stats.append({
                'team_id': team.id,
                'team_name': team.team_name,
                'total_members': len(team_participants),
                'checked_in': team_checked_in,
                'checkin_percentage': round((team_checked_in / len(team_participants) * 100) if len(team_participants) > 0 else 0, 1)
            })

    # Recent check-ins for this event
    recent_checkins = CheckinLog.query.filter_by(
        event_id=event_id
    ).order_by(CheckinLog.checked_in_at.desc()).limit(10).all()

    recent_activity = []
    for log in recent_checkins:
        participant = Participant.query.get(log.participant_id)
        if participant:
            recent_activity.append({
                'participant_name': participant.name,
                'participant_email': participant.email,
                'checked_in_at': log.checked_in_at.isoformat(),
                'checked_in_by': str(log.checked_in_by) if log.checked_in_by else 'Self check-in'
            })

    return jsonify({
        'event': {
            'id': str(event.id),
            'name': event.name,
            'date': event.date.isoformat(),
            'venue': event.venue,
            'mode': event.mode
        },
        'stats': {
            'total_participants': total_participants,
            'checked_in': checked_in,
            'not_checked_in': not_checked_in,
            'checkin_percentage': checkin_percentage
        },
        'teams_stats': teams_stats,
        'recent_activity': recent_activity
    })
