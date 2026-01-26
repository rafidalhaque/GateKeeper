# CSV Import with Custom Fields - Guide

## Overview

GateKeeper supports importing participants via CSV with full support for event-specific custom fields. This allows bulk participant registration with all required data in one import.

---

## Quick Start

1. **Configure Custom Fields** (if needed)
   - Go to Event Detail → "Configure Fields & Schedule"
   - Add custom fields (e.g., dietary_preference, t_shirt_size)
   - Save configuration

2. **Download Template**
   - Go to Event Detail → "Import CSV"
   - Click "Download CSV Template"
   - Template includes all standard + custom fields

3. **Fill CSV**
   - Open template in Excel/LibreOffice/Google Sheets
   - Fill participant data
   - Include values for custom fields

4. **Import**
   - Upload CSV file
   - System validates and imports
   - Shows success count + any errors

---

## CSV Format

### Solo Mode Events

**Required Columns:**
- `participant_name`
- `participant_email`

**Optional Columns:**
- `t_shirt_size`
- Any custom field names configured for the event

**Example:**
```csv
participant_name,participant_email,t_shirt_size,dietary_preference,emergency_contact
John Doe,john@example.com,L,Halal,+1234567890
Jane Smith,jane@example.com,M,Vegetarian,+0987654321
```

### Team Mode Events

**Required Columns:**
- `team_id` (unique identifier for grouping)
- `team_name`
- `member_name`
- `member_email`

**Optional Columns:**
- `t_shirt_size`
- Any custom field names configured for the event

**Example:**
```csv
team_id,team_name,member_name,member_email,t_shirt_size,dietary_preference
TEAM001,Team Alpha,John Doe,john@example.com,L,Halal
TEAM001,Team Alpha,Jane Smith,jane@example.com,M,Vegetarian
TEAM002,Team Beta,Bob Johnson,bob@example.com,XL,None
```

---

## Custom Fields Integration

### How It Works

1. **System reads event's `custom_fields` configuration**
   ```json
   [
     {"name": "dietary_preference", "label": "Dietary Preference", "type": "select"},
     {"name": "emergency_contact", "label": "Emergency Contact", "type": "text"}
   ]
   ```

2. **During import, extracts matching columns**
   - Standard columns (name, email, etc.) → standard fields
   - Columns matching custom field names → stored in `custom_data` JSONB

3. **Stored in participant record**
   ```json
   {
     "name": "John Doe",
     "email": "john@example.com",
     "custom_data": {
       "dietary_preference": "Halal",
       "emergency_contact": "+1234567890"
     }
   }
   ```

### Column Naming Rules

- Must **exactly match** custom field `name` (not `label`)
- Case-sensitive
- Use underscores, no spaces (e.g., `emergency_contact` not `Emergency Contact`)

### Custom Field Types

All field types are supported in CSV import:

| Field Type | CSV Value Example |
|------------|-------------------|
| Text | `John Doe` |
| Email | `john@example.com` |
| Number | `25` |
| Select | `Option A` (must match defined option) |
| Checkbox | `Yes` or `No` |
| Textarea | `Long text content here` |

---

## Validation & Error Handling

### Validation Rules

1. **Required Fields**
   - Standard required fields must be present
   - Custom fields marked as required → validation in frontend/API (not CSV import)

2. **Duplicate Detection**
   - Participants with same email in same event → skipped with warning
   - Teams with same name → merged (participants added to existing team)

3. **Empty Values**
   - Empty custom field values → stored as `null`
   - Missing columns → no data stored for that field

### Error Reporting

Import returns:
```json
{
  "success": true,
  "imported_count": 45,
  "errors": [
    "Row 12: Duplicate email john@example.com (skipped)",
    "Row 23: Missing team_id"
  ]
}
```

---

## Examples

### Example 1: Islamic Event with Dietary & Section

**Custom Fields Configuration:**
```json
[
  {"name": "dietary_preference", "type": "select", "options": "Halal, Vegetarian, Vegan"},
  {"name": "section", "type": "select", "options": "Brothers, Sisters, Family"}
]
```

**CSV:**
```csv
participant_name,participant_email,dietary_preference,section
Ahmed Khan,ahmed@example.com,Halal,Brothers
Fatima Ali,fatima@example.com,Halal,Sisters
```

### Example 2: Youth Conference with T-Shirt & Emergency

**Custom Fields Configuration:**
```json
[
  {"name": "t_shirt_size", "type": "select", "options": "XS, S, M, L, XL"},
  {"name": "emergency_contact", "type": "text", "required": true},
  {"name": "medical_conditions", "type": "textarea"}
]
```

**CSV:**
```csv
participant_name,participant_email,t_shirt_size,emergency_contact,medical_conditions
John Doe,john@example.com,L,+1234567890,None
Jane Smith,jane@example.com,M,+0987654321,Asthma
```

### Example 3: Team Tournament with Custom Fields

**Custom Fields Configuration:**
```json
[
  {"name": "player_role", "type": "select", "options": "Captain, Player, Reserve"},
  {"name": "jersey_number", "type": "number"}
]
```

**CSV:**
```csv
team_id,team_name,member_name,member_email,player_role,jersey_number
TEAM001,Warriors,Ahmed,ahmed@example.com,Captain,10
TEAM001,Warriors,Bilal,bilal@example.com,Player,7
TEAM002,Champions,Umar,umar@example.com,Captain,9
```

---

## Advanced Features

### Auto-Generated Template

Download button generates CSV template with:
- All required columns based on event mode
- All custom field columns
- Example row with sample data
- Comments/guidance

### Batch Processing

- Uses Celery for background processing
- Handles large CSV files (1000+ participants)
- Progress tracking via job status API

### Data Integrity

- Transaction-based import (all or nothing per commit)
- Duplicate prevention
- Foreign key validation (teams, events)
- Rollback on critical errors

---

## Troubleshooting

### Common Issues

**Issue:** Custom field data not imported
- **Solution:** Ensure column name exactly matches field `name` in configuration

**Issue:** "Missing required headers" error
- **Solution:** Check CSV has all required columns for event mode

**Issue:** Duplicate participants skipped
- **Solution:** Remove duplicates from CSV or delete existing participants first

**Issue:** Import hangs/times out
- **Solution:** CSV import runs in background. Check job status via API

### Testing Import

1. Start with small CSV (2-3 participants)
2. Verify data imported correctly
3. Check `custom_data` field in database
4. Then proceed with full import

---

## API Reference

### Import CSV
```http
POST /api/import/csv
Content-Type: multipart/form-data

file: <csv_file>
event_id: <uuid>
```

### Check Import Status
```http
GET /api/import/status/<job_id>
```

### Download Template
```http
GET /admin/events/<event_id>/csv-template
```

---

## Database Schema

### Participant Model

```python
class Participant(db.Model):
    id = UUID
    event_id = UUID
    name = String
    email = String
    t_shirt_size = String
    custom_data = JSONB  # <-- Custom field values stored here
    # ... other fields
```

### Custom Data Storage

```json
{
  "dietary_preference": "Halal",
  "emergency_contact": "+1234567890",
  "section": "Brothers",
  "medical_conditions": "None"
}
```

---

## Best Practices

1. **Configure fields before import**
   - Set up all custom fields first
   - Then generate and use template

2. **Use consistent naming**
   - Snake_case for field names
   - No spaces, special characters

3. **Test with sample**
   - Import 2-3 records first
   - Verify all data correct
   - Then full import

4. **Keep backups**
   - Export existing data before large imports
   - Can rollback if needed

5. **Validate in spreadsheet**
   - Check for duplicates
   - Ensure all required fields filled
   - Format consistency

---

## Related Documentation

- [Custom Fields Configuration](./CUSTOM_FIELDS_SCHEDULE_IMPLEMENTATION.md)
- [Event Management](./plan.md)
- [API Documentation](./API.md)

---

**Last Updated:** January 26, 2026
**Status:** ✅ Fully Implemented
