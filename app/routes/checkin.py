"""
Check-in and attendance routes
"""
from flask import Blueprint, request, jsonify, g
from app.models import db
from app.models.events import Participant, Event, CheckinLog
from app.models.settings import AppSettings
from app.utils.auth import login_required, permission_required, get_current_user
from datetime import datetime
from app.services.token_service import render_token_template

bp = Blueprint('checkin', __name__, url_prefix='/api/checkin')


@bp.route('/lookup/<uuid:unique_uuid>', methods=['GET'])
def lookup_participant(unique_uuid):
    """Lookup participant by unique UUID (public endpoint with auth-aware behavior)"""
    participant = Participant.query.filter_by(unique_url_uuid=unique_uuid).first_or_404()
    
    event = Event.query.get(participant.event_id)
    
    # Check if user is authenticated
    current_user = get_current_user()
    
    response = {
        'id': str(participant.id),
        'unique_url_uuid': str(participant.unique_url_uuid),
        'name': participant.name,
        'email': participant.email,
        'custom_data': participant.custom_data,
        'attendance_status': participant.attendance_status,
        'attended_at': participant.attended_at.isoformat() if participant.attended_at else None,
        'event': {
            'id': str(event.id),
            'name': event.name,
            'date': event.date.isoformat(),
            'venue': event.venue,
            'mode': event.mode
        }
    }
    
    # Add team info if applicable
    if participant.team:
        response['team'] = {
            'id': participant.team.id,
            'uuid': str(participant.team.uuid),
            'team_name': participant.team.team_name
        }
    
    # Indicate if user is authenticated (no passcode required)
    response['is_authenticated'] = current_user is not None
    response['requires_passcode'] = current_user is None and event.passcode is not None
    
    return jsonify(response)


@bp.route('/confirm', methods=['POST'])
def confirm_checkin():
    """Confirm check-in (auth-aware: no passcode if authenticated)"""
    data = request.get_json()
    
    # Validate required fields
    if 'unique_uuid' not in data:
        return jsonify({'error': 'Missing unique_uuid'}), 400
    
    participant = Participant.query.filter_by(unique_url_uuid=data['unique_uuid']).first_or_404()
    event = Event.query.get(participant.event_id)
    
    # Check authentication status
    current_user = get_current_user()
    
    # If not authenticated and event has passcode, validate it
    if not current_user:
        if event.passcode:
            if 'passcode' not in data or data['passcode'] != event.passcode:
                return jsonify({'error': 'Invalid passcode'}), 403
    else:
        # Authenticated user must have permission
        if not current_user.has_permission('attendance.mark'):
            return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Check if already checked in
    if participant.attendance_status:
        return jsonify({
            'message': 'Already checked in',
            'attended_at': participant.attended_at.isoformat()
        }), 200
    
    # Mark attendance
    participant.attendance_status = True
    participant.attended_at = datetime.utcnow()
    
    # Create check-in log
    checkin_log = CheckinLog(
        participant_id=participant.id,
        event_id=event.id,
        checked_in_by=current_user.id if current_user else None,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        device_fingerprint=data.get('device_fingerprint')
    )
    
    db.session.add(checkin_log)
    db.session.commit()
    
    # Check if token printing is enabled in settings
    token_printing_enabled = AppSettings.get('token_printing_enabled', 'true')
    if isinstance(token_printing_enabled, str):
        token_printing_enabled = token_printing_enabled.lower() == 'true'

    # Determine if we should print the token
    should_print = False
    print_html = None
    
    # Only proceed with printing logic if token printing is enabled
    if token_printing_enabled:
        # Logic:
        # 1. Solo participants always print
        # 2. Team participants print ONLY if they are the first member to check in

        if not participant.team_id:
            # Solo participant
            should_print = True
        else:
            # Team participant - check if any OTHER member of the team is already checked in
            # We query for other members of the same team who have attendance_status=True
            # excluding the current participant (who we just marked as true, so we check if count > 1)

            # Count checked-in members for this team
            checked_in_count = Participant.query.filter(
                Participant.team_id == participant.team_id,
                Participant.attendance_status == True
            ).count()

            # If count is 1, it means ONLY the current participant is checked in (so they are the first)
            if checked_in_count == 1:
                should_print = True

        if should_print:
            try:
                print_html = render_token_template(event, participant)
            except Exception as e:
                # Log error but don't fail the check-in
                print(f"Error generating token HTML: {e}")
                should_print = False

    return jsonify({
        'message': 'Check-in successful',
        'participant_id': str(participant.id),
        'name': participant.name,
        'attended_at': participant.attended_at.isoformat(),
        'should_print': should_print,
        'print_html': print_html
    }), 200


@bp.route('/logs', methods=['GET'])
@permission_required('attendance.read')
def get_checkin_logs():
    """Get check-in logs for an event"""
    event_id = request.args.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Missing event_id parameter'}), 400
    
    logs = CheckinLog.query.filter_by(event_id=event_id).order_by(CheckinLog.checked_in_at.desc()).all()
    
    return jsonify([{
        'id': log.id,
        'participant_id': str(log.participant_id),
        'participant_name': log.participant.name if log.participant else None,
        'team_name': log.participant.team.team_name if log.participant and log.participant.team else None,
        'checked_in_by': str(log.checked_in_by) if log.checked_in_by else 'Self check-in',
        'ip_address': log.ip_address,
        'checked_in_at': log.checked_in_at.isoformat()
    } for log in logs])
