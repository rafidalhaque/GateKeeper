"""
CSV import service
"""
import csv
import io
import uuid
from app.models import db
from app.models.events import Event, Team, Participant


def validate_csv_format(event, csv_content):
    """Validate CSV format based on event mode"""
    reader = csv.DictReader(io.StringIO(csv_content))
    headers = reader.fieldnames
    
    if event.mode == 'team':
        required_headers = ['team_id', 'team_name', 'member_name', 'member_email']
        missing = [h for h in required_headers if h not in headers]
        if missing:
            return False, f"Missing required headers: {', '.join(missing)}"
    
    elif event.mode == 'solo':
        required_headers = ['participant_name', 'participant_email']
        missing = [h for h in required_headers if h not in headers]
        if missing:
            return False, f"Missing required headers: {', '.join(missing)}"
    
    return True, "Valid"


def process_csv_import(event_id, csv_content):
    """Process CSV import for an event"""
    from app.app import create_app
    app = create_app()
    
    with app.app_context():
        event = Event.query.get(event_id)
        if not event:
            return {'success': False, 'error': 'Event not found'}
        
        # Validate CSV format
        valid, message = validate_csv_format(event, csv_content)
        if not valid:
            return {'success': False, 'error': message}
        
        reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        errors = []
        
        if event.mode == 'team':
            # Group by team_id
            teams_data = {}
            for row in reader:
                team_id = row.get('team_id')
                if team_id not in teams_data:
                    teams_data[team_id] = {
                        'team_name': row.get('team_name'),
                        'members': []
                    }
                teams_data[team_id]['members'].append({
                    'name': row.get('member_name'),
                    'email': row.get('member_email'),
                    't_shirt_size': row.get('t-shirt_size', row.get('t_shirt_size'))
                })
            
            # Create teams and participants
            for team_id, team_data in teams_data.items():
                # Check if team already exists
                team = Team.query.filter_by(event_id=event_id).filter(
                    Team.team_name == team_data['team_name']
                ).first()
                
                if not team:
                    team = Team(
                        event_id=event_id,
                        team_name=team_data['team_name']
                    )
                    db.session.add(team)
                    db.session.flush()  # Get team ID
                
                # Add members
                for member in team_data['members']:
                    participant = Participant(
                        event_id=event_id,
                        team_id=team.id,
                        name=member['name'],
                        email=member['email'],
                        t_shirt_size=member.get('t_shirt_size')
                    )
                    db.session.add(participant)
                    imported_count += 1
                
                # Update team is_empty flag
                team.is_empty = False
        
        elif event.mode == 'solo':
            for row in reader:
                participant = Participant(
                    event_id=event_id,
                    name=row.get('participant_name'),
                    email=row.get('participant_email'),
                    t_shirt_size=row.get('t-shirt_size', row.get('t_shirt_size'))
                )
                db.session.add(participant)
                imported_count += 1
        
        try:
            db.session.commit()
            return {
                'success': True,
                'imported_count': imported_count,
                'errors': errors
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
