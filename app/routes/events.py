"""
Event management routes
"""
from flask import Blueprint, request, jsonify, g
from app.models import db
from app.models.events import Event
from app.utils.auth import login_required, permission_required
from datetime import datetime
import uuid

bp = Blueprint('events', __name__, url_prefix='/api/events')


@bp.route('', methods=['POST'])
@permission_required('event.create')
def create_event():
    """Create a new event"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'date', 'mode']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate mode
    if data['mode'] not in ['solo', 'team']:
        return jsonify({'error': 'Invalid mode. Must be "solo" or "team"'}), 400
    
    # Parse date
    try:
        event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Create event
    event = Event(
        name=data['name'],
        date=event_date,
        venue=data.get('venue'),
        mode=data['mode'],
        passcode=data.get('passcode'),
        ticket_template_html=data.get('ticket_template_html'),
        ticket_template_css=data.get('ticket_template_css'),
        custom_fields=data.get('custom_fields'),
        schedule_config=data.get('schedule_config')
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'id': str(event.id),
        'name': event.name,
        'date': event.date.isoformat(),
        'venue': event.venue,
        'mode': event.mode,
        'created_at': event.created_at.isoformat()
    }), 201


@bp.route('', methods=['GET'])
@permission_required('event.read')
def list_events():
    """List all events"""
    events = Event.query.order_by(Event.date.desc()).all()
    
    return jsonify([{
        'id': str(event.id),
        'name': event.name,
        'date': event.date.isoformat(),
        'venue': event.venue,
        'mode': event.mode,
        'created_at': event.created_at.isoformat()
    } for event in events])


@bp.route('/<uuid:event_id>', methods=['GET'])
@permission_required('event.read')
def get_event(event_id):
    """Get a specific event"""
    event = Event.query.get_or_404(event_id)
    
    return jsonify({
        'id': str(event.id),
        'name': event.name,
        'date': event.date.isoformat(),
        'venue': event.venue,
        'mode': event.mode,
        'passcode': event.passcode,
        'ticket_template_html': event.ticket_template_html,
        'ticket_template_css': event.ticket_template_css,
        'custom_fields': event.custom_fields,
        'schedule_config': event.schedule_config,
        'created_at': event.created_at.isoformat(),
        'updated_at': event.updated_at.isoformat()
    })


@bp.route('/<uuid:event_id>', methods=['PUT'])
@permission_required('event.update')
def update_event(event_id):
    """Update an event"""
    event = Event.query.get_or_404(event_id)
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        event.name = data['name']
    if 'date' in data:
        try:
            event.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    if 'venue' in data:
        event.venue = data['venue']
    if 'mode' in data:
        if data['mode'] not in ['solo', 'team']:
            return jsonify({'error': 'Invalid mode'}), 400
        event.mode = data['mode']
    if 'passcode' in data:
        event.passcode = data['passcode']
    if 'ticket_template_html' in data:
        event.ticket_template_html = data['ticket_template_html']
    if 'ticket_template_css' in data:
        event.ticket_template_css = data['ticket_template_css']
    if 'custom_fields' in data:
        event.custom_fields = data['custom_fields']
    if 'schedule_config' in data:
        event.schedule_config = data['schedule_config']
    
    db.session.commit()
    
    return jsonify({
        'id': str(event.id),
        'name': event.name,
        'date': event.date.isoformat(),
        'venue': event.venue,
        'mode': event.mode,
        'updated_at': event.updated_at.isoformat()
    })


@bp.route('/<uuid:event_id>', methods=['DELETE'])
@permission_required('event.delete')
def delete_event(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({'message': 'Event deleted successfully'}), 200
