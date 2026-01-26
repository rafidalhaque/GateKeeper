# Custom Fields & Schedule Configuration - Quick Guide

## ✅ Feature Implemented

Per-event custom fields and schedule configuration system as specified in plan.md.

---

## Quick Access

### Configuration Page
```
/admin/events/{event_id}/configure
```

### How to Access
1. Go to event detail page
2. Click **"Configure Fields & Schedule"** button
3. Configure and save

---

## Features

### Custom Fields
- **6 field types:** Text, Email, Number, Select, Checkbox, Textarea
- **Quick templates:** Dietary, T-Shirt, Gender Section, Emergency Contact, Allergies, Volunteer
- **Configurable:** Name, Label, Type, Required, Options, Placeholder

### Schedule Configuration
- **Prayer Times:** Fajr, Dhuhr, Asr, Maghrib, Isha
- **Event Program:** Timeline with time + activity
- **Breaks:** Name, start time, duration

### Preview Tab
- Visual preview of all configuration
- Prayer times grid
- Program timeline
- Raw JSON view

---

## Database Storage

### Custom Fields
Stored in `events.custom_fields` (JSONB):
```json
[
  {
    "name": "dietary_preference",
    "label": "Dietary Preference",
    "type": "select",
    "required": false,
    "options": "Halal, Vegetarian, Vegan",
    "placeholder": "Select your preference"
  }
]
```

### Schedule Config
Stored in `events.schedule_config` (JSONB):
```json
{
  "prayer_times": {"fajr": "05:30", "dhuhr": "13:15", ...},
  "program": [{"time": "18:30", "activity": "Registration"}],
  "breaks": [{"name": "Prayer Break", "start": "13:15", "duration": 30}]
}
```

### Participant Data
Custom field values stored in `participants.custom_data` (JSONB):
```json
{
  "dietary_preference": "Halal",
  "t_shirt_size": "L",
  "emergency_contact": "+1234567890"
}
```

---

## Integration Points

### Current
- ✅ Configuration UI
- ✅ API endpoints (GET/PUT)
- ✅ Preview system
- ✅ **CSV Import with Custom Fields**

### Future (Ready for Integration)
- ⏳ Dynamic registration forms (will use custom_fields)
- ⏳ Ticket templates (placeholders for custom fields)
- ⏳ Email templates (placeholders for schedule)
- ⏳ Reports (export custom field data)

---

## CSV Import

Custom fields are fully integrated with CSV import:

1. **Download Template**: Auto-generates CSV with all custom field columns
2. **Import Data**: System maps CSV columns to custom fields
3. **Storage**: Values stored in `participants.custom_data` JSONB

**Example:**
```csv
participant_name,participant_email,dietary_preference,emergency_contact
John Doe,john@example.com,Halal,+1234567890
```

**See:** `docs/CSV_IMPORT_WITH_CUSTOM_FIELDS.md` for complete guide

---

## Examples

### Islamic Event (Ramadan Iftar)
```json
{
  "custom_fields": [
    {"name": "dietary_preference", "type": "select", "options": "Halal, Vegetarian"},
    {"name": "section", "type": "select", "options": "Brothers, Sisters, Family", "required": true}
  ],
  "schedule_config": {
    "prayer_times": {"maghrib": "18:45", "isha": "20:30"},
    "program": [
      {"time": "18:30", "activity": "Registration"},
      {"time": "18:45", "activity": "Maghrib & Iftar"},
      {"time": "19:30", "activity": "Maghrib Prayer"}
    ]
  }
}
```

### Youth Conference
```json
{
  "custom_fields": [
    {"name": "t_shirt_size", "type": "select", "options": "XS, S, M, L, XL", "required": true},
    {"name": "emergency_contact", "type": "text", "required": true}
  ],
  "schedule_config": {
    "prayer_times": {"dhuhr": "13:00", "asr": "16:30"},
    "breaks": [
      {"name": "Lunch & Dhuhr", "start": "13:00", "duration": 45}
    ]
  }
}
```

---

## Files Created

1. ✅ `app/templates/admin/event_config.html` - Configuration UI
2. ✅ Route: `/admin/events/{event_id}/configure`
3. ✅ Documentation: `docs/CUSTOM_FIELDS_SCHEDULE_IMPLEMENTATION.md`

## Files Modified

1. ✅ `app/routes/frontend.py` - Added configuration route
2. ✅ `app/templates/admin/event_detail.html` - Added "Configure" button

---

## Permissions

- **Access:** `event.configure` permission or Super Admin
- **Default Roles with Access:** Super Admin, Event Admin

---

## Status

✅ **COMPLETE** - Fully functional and ready to use

**Date:** January 26, 2026  
**Specification:** plan.md Section 10 & 21
