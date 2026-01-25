# Dashboard Statistics Implementation

## Overview

The dashboard now displays comprehensive statistics including:
- **Total Events**: Count of all events in the system
- **Total Participants**: Count of all participants across all events  
- **Total Check-ins**: Count of all participants who have checked in (all time)
- **Check-ins per Event**: Detailed table showing check-in statistics for each event

## Changes Made

### 1. New API Endpoint: `/api/stats/dashboard`

**File**: `app/routes/stats.py`

This new route provides all dashboard statistics in a single API call:

```python
GET /api/stats/dashboard
Authorization: Bearer <token>
Permission Required: dashboard.view

Response:
{
  "stats": {
    "total_events": 10,
    "total_participants": 150,
    "total_checkins": 120,
    "active_events": 2,
    "checkins_today": 15
  },
  "checkins_per_event": [
    {
      "event_id": "uuid...",
      "event_name": "Tech Conference 2026",
      "checkins": 45,
      "total_participants": 50,
      "checkin_percentage": 90.0
    }
  ],
  "upcoming_events": [...],
  "recent_activity": [...]
}
```

### 2. Dashboard Statistics

The dashboard now shows:

#### Top Stats (Cards)
1. **Total Events** - All events in the system
2. **Total Participants** - All participants across all events
3. **Total Check-ins** - Total participants who have checked in (all time)

#### Check-ins per Event Table
A detailed table showing:
- Event Name (clickable link to event detail)
- Total Participants
- Checked In (badge)
- Check-in Rate (percentage)
- Progress Bar (visual representation)

#### Additional Stats
- Active Events (events happening today)
- Check-ins Today (last 24 hours)
- Upcoming Events
- Recent Activity (recent check-ins)

### 3. New Permission

**Permission**: `dashboard.view`
- **Description**: View dashboard statistics
- **Feature Group**: dashboard
- **Assigned to**: Event Admin role (and Super Admin)

### 4. Files Modified

- **`app/routes/stats.py`** (NEW)
  - Dashboard statistics endpoint
  - Event-specific statistics endpoint
  
- **`app/templates/admin/dashboard.html`**
  - Updated stats cards (removed "Active Events" card, changed to 3-column grid)
  - Added "Check-ins per Event" table
  - Updated JavaScript to use new API endpoint
  
- **`app/app.py`**
  - Registered stats blueprint
  
- **`app/cli.py`**
  - Added `dashboard.view` permission to seed data
  - Added permission to Event Admin role

## Database Queries

The stats API uses efficient queries:

```python
# Total events
Event.query.count()

# Total participants
Participant.query.count()

# Total check-ins
Participant.query.filter_by(attendance_status=True).count()

# Check-ins per event (with JOIN)
db.session.query(
    Event.id,
    Event.name,
    func.count(Participant.id).filter(Participant.attendance_status == True).label('checkins'),
    func.count(Participant.id).label('total_participants')
).outerjoin(Participant, Event.id == Participant.event_id)\
 .group_by(Event.id, Event.name)\
 .all()
```

## How to Test

### 1. Ensure Permission is Seeded

```bash
flask --app run.py seed-permissions
```

### 2. Add Permission to Your User's Role

The permission should already be added to Event Admin role. Verify:

```python
from app.app import create_app
from app.models.auth import Role

app = create_app()
with app.app_context():
    role = Role.query.filter_by(name='Event Admin').first()
    print([p.key for p in role.permissions])
```

Should include `dashboard.view`.

### 3. Access the Dashboard

1. Navigate to: `http://localhost:5000/admin`
2. You should see:
   - Three stat cards at the top (Total Events, Total Participants, Total Check-ins)
   - Quick Actions section
   - **Check-ins per Event** table with all events and their check-in statistics
   - Recent Activity and Upcoming Events sections

### 4. Test the API Directly

```bash
# Get auth token first (login via browser, check DevTools)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/stats/dashboard
```

## Check-ins per Event Table Features

The table displays:
- **Event Name**: Links to event detail page
- **Total Participants**: Count of all registered participants
- **Checked In**: Green badge showing number of check-ins
- **Check-in Rate**: Percentage (e.g., "90.0%")
- **Progress Bar**: Visual green progress bar showing check-in completion

### Example Output

```
Event Name              | Total Participants | Checked In | Check-in Rate | Progress
------------------------|-------------------|------------|---------------|----------
Tech Conference 2026    | 50                | 45         | 90.0%         | [████████░░]
Hackathon 2026          | 30                | 15         | 50.0%         | [█████░░░░░]
Workshop Series         | 20                | 20         | 100.0%        | [██████████]
```

## API Endpoints

### Dashboard Statistics
```http
GET /api/stats/dashboard
Authorization: Bearer <token>
Permission: dashboard.view

Returns comprehensive dashboard statistics including:
- Total counts (events, participants, check-ins)
- Check-ins per event with percentages
- Upcoming events
- Recent activity
```

### Event-Specific Statistics
```http
GET /api/stats/event/<event_id>
Authorization: Bearer <token>
Permission: dashboard.view

Returns detailed statistics for a specific event:
- Event info
- Participant counts
- Check-in statistics
- Team-wise stats (if team mode)
- Recent check-ins
```

## Performance Considerations

- All statistics are calculated on-demand from the database
- Uses efficient JOINs and aggregations
- For large datasets (1000+ events), consider adding:
  - Redis caching for dashboard stats
  - Pagination for check-ins per event table
  - Background job to pre-calculate statistics

## Future Enhancements

Potential improvements:
- [ ] Chart visualization for check-ins over time
- [ ] Export check-in statistics to CSV
- [ ] Real-time updates using WebSockets
- [ ] Filtering/sorting for check-ins per event table
- [ ] Date range selection for statistics
- [ ] Comparison between events

## Related Files

- `app/routes/stats.py` - Statistics API endpoints
- `app/templates/admin/dashboard.html` - Dashboard UI
- `app/models/events.py` - Event, Participant, CheckinLog models
- `app/cli.py` - Permission seeding
- `app/utils/auth.py` - Permission checking decorators
