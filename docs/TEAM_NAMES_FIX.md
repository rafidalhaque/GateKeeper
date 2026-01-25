# Team Names Showing "N/A" - Fix Documentation

## Date: January 26, 2026

## Issue Report
Team names were showing as "N/A" in the participants list and reports despite teams being imported correctly via CSV.

## Root Cause Analysis

The issue was in the API endpoints that return participant data. The endpoints were only returning `team_id` (an integer) but **not the full team object** with `team_name`.

### Frontend Expectation
The frontend code was trying to access:
```javascript
participant.team?.team_name || 'N/A'
```

### API Response (Before Fix)
```json
{
  "id": "uuid",
  "name": "John Doe",
  "team_id": 5,  // ❌ Only ID, no team object
  "email": "john@example.com"
}
```

### API Response (After Fix)
```json
{
  "id": "uuid",
  "name": "John Doe",
  "team_id": 5,
  "team": {  // ✅ Full team object included
    "id": 5,
    "team_name": "Team Alpha",
    "uuid": "team-uuid"
  },
  "email": "john@example.com"
}
```

---

## Solution

### 1. Fixed Participants List API

**File:** `app/routes/participants.py`

**Endpoint:** `GET /api/participants`

**Change:**
Added team relationship data to the JSON response:

```python
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
    } if p.team else None,  # ✅ Added this
    'attendance_status': p.attendance_status,
    'attended_at': p.attended_at.isoformat() if p.attended_at else None,
    'unique_url_uuid': str(p.unique_url_uuid),
    't_shirt_size': p.t_shirt_size
} for p in participants])
```

### 2. Fixed Checkin Logs API

**File:** `app/routes/checkin.py`

**Endpoint:** `GET /api/checkin/logs`

**Change:**
Added `team_name` to checkin logs response:

```python
return jsonify([{
    'id': log.id,
    'participant_id': str(log.participant_id),
    'participant_name': log.participant.name if log.participant else None,
    'team_name': log.participant.team.team_name if log.participant and log.participant.team else None,  # ✅ Added this
    'checked_in_by': str(log.checked_in_by) if log.checked_in_by else 'Self check-in',
    'ip_address': log.ip_address,
    'checked_in_at': log.checked_in_at.isoformat()
} for log in logs])
```

---

## How It Works

### Database Relationship
The `Participant` model has a relationship to `Team`:

```python
class Participant(db.Model):
    team_id = db.Column(Integer, ForeignKey('teams.id', ondelete='SET NULL'))
    team = relationship('Team', back_populates='participants')
```

### Accessing Team Data
When you access `participant.team`, SQLAlchemy automatically fetches the related team:

```python
if p.team:
    team_name = p.team.team_name  # ✅ Works because of relationship
```

### Frontend Access
The frontend can now access the team name:

```javascript
// Before: participant.team?.team_name was undefined
// After: participant.team?.team_name works correctly

<td x-text="participant.team?.team_name || 'N/A'"></td>
```

---

## CSV Import Process

The CSV import already creates teams correctly:

```python
# From app/services/csv_import.py
team = Team(
    event_id=event_id,
    team_name=team_data['team_name']
)
db.session.add(team)
db.session.flush()  # Get team ID

participant = Participant(
    event_id=event_id,
    team_id=team.id,  # ✅ Team is linked
    name=member['name'],
    email=member['email']
)
```

The import was working correctly. The issue was only in the API responses not including the team data.

---

## Testing

### Manual Test
1. Import CSV with teams
2. Navigate to `/admin/participants` or `/admin/events/{event_id}`
3. Check participants list
4. **Result:** Team names now show correctly instead of "N/A"

### Expected Behavior

**Solo Mode Event:**
- Team column shows "N/A" ✅ (expected)

**Team Mode Event:**
- Team column shows actual team name ✅ (e.g., "Team Alpha")

---

## Files Modified

1. ✅ `app/routes/participants.py` - Added team object to response
2. ✅ `app/routes/checkin.py` - Added team_name to checkin logs

---

## Impact

### Before Fix
- ❌ Participants list showed "N/A" for all team names
- ❌ Reports showed "N/A" for team names
- ❌ Event detail page showed "N/A" for teams
- ✅ CSV import worked correctly (teams were created)
- ✅ Database had correct team associations

### After Fix
- ✅ Participants list shows actual team names
- ✅ Reports show team names correctly
- ✅ Event detail page shows team names
- ✅ CSV import continues to work
- ✅ Solo mode participants still show "N/A" (as expected)

---

## Frontend Template References

These templates already had the correct code to display team names:

1. **`app/templates/admin/participants.html`**
   ```html
   <td x-text="participant.team?.team_name || 'N/A'"></td>
   ```

2. **`app/templates/admin/event_detail.html`**
   ```html
   <td x-text="participant.team?.team_name || 'N/A'"></td>
   ```

3. **`app/templates/admin/reports.html`**
   ```html
   <td x-text="checkin.team_name || 'N/A'"></td>
   ```

The frontend code was correct; it just needed the API to provide the data!

---

## Why This Fix Works

### SQLAlchemy Relationships
SQLAlchemy's `relationship()` allows easy access to related objects:

```python
# Single query gets participant
participant = Participant.query.get(id)

# Accessing .team automatically fetches from database
team_name = participant.team.team_name  # ✅ Works!
```

### Conditional Serialization
We check if team exists before accessing it:

```python
'team': {
    'id': p.team.id,
    'team_name': p.team.team_name,
    'uuid': str(p.team.uuid)
} if p.team else None  # ✅ Returns None for solo participants
```

---

## Notes

- Solo mode participants have `team_id = None`, so `p.team` is `None`
- The `|| 'N/A'` in JavaScript handles the None/null case
- Team relationships are properly loaded via SQLAlchemy
- No database schema changes were needed
- CSV import logic didn't need changes

---

## Status

✅ **FIXED** - Team names now display correctly in all views

**Fixed By:** GitHub Copilot  
**Date:** January 26, 2026  
**Affected Endpoints:** `/api/participants`, `/api/checkin/logs`  
**Root Cause:** Missing team object in API responses
