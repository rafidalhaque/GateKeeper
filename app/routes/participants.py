"""
Participant management routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import Event, Participant, Team
from app.utils.auth import permission_required

bp = Blueprint('participants', __name__, url_prefix='/api/participants')


@bp.route('', methods=['POST'])
@permission_required('participant.create')
def create_participant():
    """Create a new participant"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['event_id', 'name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate event exists
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Create participant
    participant = Participant(
        event_id=data['event_id'],
        team_id=data.get('team_id'),
        name=data['name'],
        email=data['email'],
        custom_data=data.get('custom_data')
    )
    
    db.session.add(participant)
    
    # Update team is_empty flag if team is assigned
    if participant.team_id:
        team = Team.query.get(participant.team_id)
        if team and team.is_empty:
            team.is_empty = False
    
    db.session.commit()
    
    return jsonify({
        'id': str(participant.id),
        'name': participant.name,
        'email': participant.email,
        'unique_url_uuid': str(participant.unique_url_uuid),
        'created_at': participant.created_at.isoformat()
    }), 201


@bp.route('', methods=['GET'])
@permission_required('participant.read')
def list_participants():
    """List participants with optional event filter"""
    event_id = request.args.get('event_id')
    
    query = Participant.query
    
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    participants = query.all()
    
    return jsonify([{
        'id': str(p.id),
        'name': p.name,
        'email': p.email,
        'event_id': str(p.event_id),
        'team_id': p.team_id,
        'team': {
            'id': p.team.id,
            'team_name': p.team.team_name,
            'uuid': str(p.team.uuid)
        } if p.team else None,
        'attendance_status': p.attendance_status,
        'attended_at': p.attended_at.isoformat() if p.attended_at else None,
        'unique_url_uuid': str(p.unique_url_uuid),
        'custom_data': p.custom_data
    } for p in participants])


@bp.route('/<uuid:participant_id>', methods=['PUT'])
@permission_required('participant.update')
def update_participant(participant_id):
    """Update a participant"""
    participant = Participant.query.get_or_404(participant_id)
    data = request.get_json()
    
    old_team_id = participant.team_id
    
    # Update fields
    if 'name' in data:
        participant.name = data['name']
    if 'email' in data:
        participant.email = data['email']
    if 'custom_data' in data:
        participant.custom_data = data['custom_data']
    if 'team_id' in data:
        participant.team_id = data['team_id']
    
    db.session.commit()
    
    # Update team is_empty flags if team changed
    if old_team_id != participant.team_id:
        # Check old team
        if old_team_id:
            old_team = Team.query.get(old_team_id)
            if old_team and len(old_team.participants) == 0:
                old_team.is_empty = True
        
        # Check new team
        if participant.team_id:
            new_team = Team.query.get(participant.team_id)
            if new_team and new_team.is_empty:
                new_team.is_empty = False
        
        db.session.commit()
    
    return jsonify({
        'id': str(participant.id),
        'name': participant.name,
        'email': participant.email,
        'updated_at': participant.updated_at.isoformat()
    })


@bp.route('/<uuid:participant_id>', methods=['DELETE'])
@permission_required('participant.delete')
def delete_participant(participant_id):
    """Delete a participant"""
    participant = Participant.query.get_or_404(participant_id)
    team_id = participant.team_id
    
    db.session.delete(participant)
    db.session.commit()
    
    # Update team is_empty flag if applicable
    if team_id:
        team = Team.query.get(team_id)
        if team and len(team.participants) == 0:
            team.is_empty = True
            db.session.commit()
    
    return jsonify({'message': 'Participant deleted successfully'}), 200
