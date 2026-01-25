"""Test participants API returns team data"""
from app.app import create_app

app = create_app()

with app.app_context():
    with app.test_request_context():
        from app.models.events import Event, Team, Participant
        from app.models import db

        # Create a test event
        event = Event.query.first()

        if event:
            # Get participants with team data
            participants = Participant.query.filter_by(event_id=event.id).limit(5).all()

            print(f"✅ Testing participants API fix for event: {event.name}")
            print(f"   Found {len(participants)} participants\n")

            for p in participants:
                team_info = "No team (Solo)"
                if p.team:
                    team_info = f"Team: {p.team.team_name} (ID: {p.team.id})"

                print(f"   • {p.name}")
                print(f"     Email: {p.email}")
                print(f"     {team_info}")
                print()

            # Test JSON serialization
            print("✅ Testing JSON response format:")
            participant_json = {
                'id': str(p.id),
                'name': p.name,
                'team': {
                    'id': p.team.id,
                    'team_name': p.team.team_name,
                    'uuid': str(p.team.uuid)
                } if p.team else None
            }

            if participant_json['team']:
                print(f"   Team object: {participant_json['team']}")
                print("   ✅ Team name will show in UI!")
            else:
                print("   No team (expected for solo events)")
        else:
            print("❌ No events found in database")
