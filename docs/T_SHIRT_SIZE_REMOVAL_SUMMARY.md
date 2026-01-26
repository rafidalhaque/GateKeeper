# T-Shirt Size Removed from Database Schema

**Date:** January 26, 2026  
**Status:** ✅ COMPLETE

---

## Problem

The `t_shirt_size` field existed as both:
1. A standard database column in `participants` table
2. A custom field in event configuration

This caused duplication in CSV templates:
```csv
participant_name,participant_email,t_shirt_size,t_shirt_size
```

---

## Solution

Removed `t_shirt_size` as a standard database column. It now exists **only** as a custom field, stored in the `custom_data` JSONB column.

---

## Changes Made

### 1. Database Migration
**File:** `migrations/versions/cc6c7b01528f_remove_t_shirt_size_column.py`

**Actions:**
- ✅ Migrates existing `t_shirt_size` data to `custom_data` JSONB
- ✅ Drops the `t_shirt_size` column
- ✅ Includes rollback support (downgrade)

**SQL executed:**
```sql
-- Move data to custom_data
UPDATE participants 
SET custom_data = 
    CASE 
        WHEN custom_data IS NULL THEN 
            jsonb_build_object('t_shirt_size', t_shirt_size)
        ELSE 
            custom_data || jsonb_build_object('t_shirt_size', t_shirt_size)
    END
WHERE t_shirt_size IS NOT NULL;

-- Drop column
ALTER TABLE participants DROP COLUMN t_shirt_size;
```

---

### 2. Model Update
**File:** `app/models/events.py`

**Before:**
```python
class Participant(db.Model):
    # ...
    t_shirt_size = db.Column(String(10))
    custom_data = db.Column(JSONB)
```

**After:**
```python
class Participant(db.Model):
    # ...
    custom_data = db.Column(JSONB)  # stores all custom fields including t_shirt_size
```

---

### 3. CSV Import Service
**File:** `app/services/csv_import.py`

**Changes:**
- ✅ Removed `t_shirt_size` from standard column lists
- ✅ It's now treated as any other custom field
- ✅ Automatically extracted and stored in `custom_data`

**Before:**
```python
standard_columns_solo = {'participant_name', 'participant_email', 't_shirt_size'}
```

**After:**
```python
standard_columns_solo = {'participant_name', 'participant_email'}
```

---

### 4. CSV Template Generator
**File:** `app/routes/frontend.py`

**Changes:**
- ✅ Removed `t_shirt_size` from default headers
- ✅ Only included if configured as custom field

**Before:**
```python
headers = ['participant_name', 'participant_email', 't_shirt_size']
```

**After:**
```python
headers = ['participant_name', 'participant_email']
# t_shirt_size added only if it's in event.custom_fields
```

---

### 5. API Routes Updated

**Files:**
- `app/routes/participants.py`
- `app/routes/checkin.py`

**Changes:**
- ✅ Removed `t_shirt_size` parameter from POST/PUT requests
- ✅ Removed `t_shirt_size` from JSON responses
- ✅ Now accessed via `custom_data.t_shirt_size`

**Before:**
```python
participant = Participant(
    name=data['name'],
    t_shirt_size=data.get('t_shirt_size'),
    custom_data=data.get('custom_data')
)

# Response
{
    'name': 'John',
    't_shirt_size': 'L',
    'custom_data': {...}
}
```

**After:**
```python
participant = Participant(
    name=data['name'],
    custom_data=data.get('custom_data')  # includes t_shirt_size
)

# Response
{
    'name': 'John',
    'custom_data': {
        't_shirt_size': 'L',
        ...
    }
}
```

---

### 6. Import Modal
**File:** `app/templates/admin/components/modals/csv_import.html`

**Changes:**
- ✅ Removed "Optional: t_shirt_size" text
- ✅ Now shows t_shirt_size only if configured as custom field

---

## Data Migration

### Existing Data
All existing `t_shirt_size` values were automatically migrated to `custom_data`:

**Before migration:**
```
participants table:
- name: "John Doe"
- t_shirt_size: "L"
- custom_data: {"emergency_contact": "+123"}
```

**After migration:**
```
participants table:
- name: "John Doe"
- custom_data: {
    "t_shirt_size": "L",
    "emergency_contact": "+123"
  }
```

---

## CSV Template Now Shows

### Solo Mode (with t_shirt_size as custom field)
```csv
participant_name,participant_email,t_shirt_size
John Doe,john@example.com,L
```

✅ **No duplication!**

### Team Mode (with t_shirt_size as custom field)
```csv
team_id,team_name,member_name,member_email,t_shirt_size
TEAM001,Warriors,John,john@example.com,L
```

---

## Benefits

1. ✅ **No duplication** - t_shirt_size appears only once
2. ✅ **Flexibility** - Can be removed/added per event
3. ✅ **Consistency** - All custom fields handled uniformly
4. ✅ **Backward compatible** - Data automatically migrated
5. ✅ **Future-proof** - Easy to add more custom fields

---

## Testing

### Verify Migration
```sql
-- Check custom_data contains t_shirt_size
SELECT id, name, custom_data->>'t_shirt_size' as t_shirt_size
FROM participants
WHERE custom_data ? 't_shirt_size';
```

### Download CSV Template
1. Go to Event Detail
2. Click "Import CSV"
3. Click "Download CSV Template"
4. Verify headers (should have t_shirt_size only once if configured)

### Import CSV
1. Fill template with data
2. Import CSV
3. Verify participants have t_shirt_size in custom_data

---

## API Changes

### Creating Participant

**Before:**
```json
POST /api/participants
{
  "name": "John",
  "email": "john@example.com",
  "t_shirt_size": "L"
}
```

**After:**
```json
POST /api/participants
{
  "name": "John",
  "email": "john@example.com",
  "custom_data": {
    "t_shirt_size": "L"
  }
}
```

### Getting Participant

**Before:**
```json
{
  "id": "...",
  "name": "John",
  "t_shirt_size": "L",
  "custom_data": {}
}
```

**After:**
```json
{
  "id": "...",
  "name": "John",
  "custom_data": {
    "t_shirt_size": "L"
  }
}
```

---

## Rollback (If Needed)

If you need to rollback:

```bash
flask --app run.py db downgrade
```

This will:
1. Re-create the `t_shirt_size` column
2. Copy data back from `custom_data`
3. Restore original schema

---

## Files Changed

1. ✅ `migrations/versions/cc6c7b01528f_remove_t_shirt_size_column.py` - NEW
2. ✅ `app/models/events.py` - Modified
3. ✅ `app/services/csv_import.py` - Modified
4. ✅ `app/routes/frontend.py` - Modified
5. ✅ `app/routes/participants.py` - Modified
6. ✅ `app/routes/checkin.py` - Modified
7. ✅ `app/templates/admin/components/modals/csv_import.html` - Modified

---

## Status

✅ **Migration completed successfully**  
✅ **All code updated**  
✅ **No errors**  
✅ **Ready for production**

---

**Now `t_shirt_size` is treated like any other custom field!**
