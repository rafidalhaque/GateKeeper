"""
CSV import service
"""
import csv
import io
from app.models import db
from app.models.events import Event, Team, Participant


def get_custom_field_names(event):
    """Extract custom field names from event configuration"""
    if not event.custom_fields:
        return set()
    return {field['name'] for field in event.custom_fields if 'name' in field}


def validate_csv_format(event, csv_content):
    """Validate CSV format based on event mode"""
    reader = csv.DictReader(io.StringIO(csv_content))
    headers = reader.fieldnames
    
    if not headers:
        return False, "CSV file is empty or has no headers"

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
    event = Event.query.get(event_id)
    if not event:
        return {'success': False, 'error': 'Event not found'}

    # Validate CSV format
    valid, message = validate_csv_format(event, csv_content)
    if not valid:
        return {'success': False, 'error': message}

    # Get custom field names for this event
    custom_field_names = get_custom_field_names(event)

    reader = csv.DictReader(io.StringIO(csv_content))

    imported_count = 0
    errors = []

    # Standard columns that are not custom fields
    # Note: t_shirt_size is now handled as a custom field, not a standard column
    standard_columns_team = {'team_id', 'team_name', 'member_name', 'member_email'}
    standard_columns_solo = {'participant_name', 'participant_email'}

    if event.mode == 'team':
        # Group by team_id
        teams_data = {}
        for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is headers
            try:
                team_id = row.get('team_id', '').strip()
                if not team_id:
                    errors.append(f"Row {row_num}: Missing team_id")
                    continue

                if team_id not in teams_data:
                    teams_data[team_id] = {
                        'team_name': row.get('team_name', '').strip(),
                        'members': []
                    }

                # Extract custom field data
                custom_data = {}
                for column_name, value in row.items():
                    # Skip standard columns
                    if column_name in standard_columns_team:
                        continue
                    # If column matches a custom field name
                    if column_name in custom_field_names:
                        custom_data[column_name] = value.strip() if value else None

                teams_data[team_id]['members'].append({
                    'name': row.get('member_name', '').strip(),
                    'email': row.get('member_email', '').strip(),
                    'custom_data': custom_data if custom_data else None
                })
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue

        # Create teams and participants
        for team_id, team_data in teams_data.items():
            try:
                # Check if team already exists
                team = Team.query.filter_by(event_id=event_id, team_name=team_data['team_name']).first()

                if not team:
                    team = Team(
                        event_id=event_id,
                        team_name=team_data['team_name']
                    )
                    db.session.add(team)
                    db.session.flush()  # Get team ID

                # Add members
                for member in team_data['members']:
                    # Check if participant already exists (by email)
                    existing = Participant.query.filter_by(
                        event_id=event_id,
                        email=member['email']
                    ).first()

                    if existing:
                        errors.append(f"Duplicate email: {member['email']} (skipped)")
                        continue

                    participant = Participant(
                        event_id=event_id,
                        team_id=team.id,
                        name=member['name'],
                        email=member['email'],
                        custom_data=member.get('custom_data')
                    )
                    db.session.add(participant)
                    imported_count += 1

                # Update team is_empty flag
                team.is_empty = False
            except Exception as e:
                errors.append(f"Team {team_id}: {str(e)}")
                continue

    elif event.mode == 'solo':
        for row_num, row in enumerate(reader, start=2):
            try:
                name = row.get('participant_name', '').strip()
                email = row.get('participant_email', '').strip()

                if not name or not email:
                    errors.append(f"Row {row_num}: Missing name or email")
                    continue

                # Check if participant already exists
                existing = Participant.query.filter_by(
                    event_id=event_id,
                    email=email
                ).first()

                if existing:
                    errors.append(f"Row {row_num}: Duplicate email {email} (skipped)")
                    continue

                # Extract custom field data
                custom_data = {}
                for column_name, value in row.items():
                    # Skip standard columns
                    if column_name in standard_columns_solo:
                        continue
                    # If column matches a custom field name
                    if column_name in custom_field_names:
                        custom_data[column_name] = value.strip() if value else None

                participant = Participant(
                    event_id=event_id,
                    name=name,
                    email=email,
                    custom_data=custom_data if custom_data else None
                )
                db.session.add(participant)
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue

    try:
        db.session.commit()
        return {
            'success': True,
            'imported_count': imported_count,
            'errors': errors if errors else []
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': str(e),
            'imported_count': 0,
            'errors': errors
        }
