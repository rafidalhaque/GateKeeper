"""
Team management routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import Event, Team
from app.utils.auth import permission_required

bp = Blueprint('teams', __name__, url_prefix='/api/teams')


@bp.route('', methods=['POST'])
@permission_required('team.create')
def create_team():
    """Create a new team"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['event_id', 'team_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate event exists
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Validate event is in team mode
    if event.mode != 'team':
        return jsonify({'error': 'Event is not in team mode'}), 400
    
    # Create team
    team = Team(
        event_id=data['event_id'],
        team_name=data['team_name']
    )
    
    db.session.add(team)
    db.session.commit()
    
    return jsonify({
        'id': team.id,
        'uuid': str(team.uuid),
        'team_name': team.team_name,
        'event_id': str(team.event_id),
        'is_empty': team.is_empty,
        'created_at': team.created_at.isoformat()
    }), 201


@bp.route('', methods=['GET'])
@permission_required('team.read')
def list_teams():
    """List teams with optional filters"""
    event_id = request.args.get('event_id')
    is_empty = request.args.get('is_empty')
    
    query = Team.query
    
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    if is_empty is not None:
        is_empty_bool = is_empty.lower() == 'true'
        query = query.filter_by(is_empty=is_empty_bool)
    
    teams = query.all()
    
    return jsonify([{
        'id': t.id,
        'uuid': str(t.uuid),
        'team_name': t.team_name,
        'event_id': str(t.event_id),
        'is_empty': t.is_empty,
        'member_count': len(t.participants)
    } for t in teams])


@bp.route('/<int:team_id>', methods=['PUT'])
@permission_required('team.update')
def update_team(team_id):
    """Update a team"""
    team = Team.query.get_or_404(team_id)
    data = request.get_json()
    
    if 'team_name' in data:
        team.team_name = data['team_name']
    
    db.session.commit()
    
    return jsonify({
        'id': team.id,
        'team_name': team.team_name,
        'updated_at': team.updated_at.isoformat()
    })


@bp.route('/<int:team_id>', methods=['DELETE'])
@permission_required('team.delete')
def delete_team(team_id):
    """Delete a team"""
    team = Team.query.get_or_404(team_id)
    
    # Check if team has members
    if len(team.participants) > 0:
        return jsonify({'error': 'Cannot delete team with members'}), 400
    
    db.session.delete(team)
    db.session.commit()
    
    return jsonify({'message': 'Team deleted successfully'}), 200


@bp.route('/bulk-delete-empty', methods=['DELETE'])
@permission_required('team.delete')
def bulk_delete_empty():
    """Bulk delete empty teams"""
    event_id = request.args.get('event_id')
    
    query = Team.query.filter_by(is_empty=True)
    
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    teams = query.all()
    count = len(teams)
    
    for team in teams:
        db.session.delete(team)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Deleted {count} empty teams',
        'count': count
    }), 200
