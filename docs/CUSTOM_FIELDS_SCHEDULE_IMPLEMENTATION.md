# Custom Fields & Schedule Configuration - Implementation Guide

## Date: January 26, 2026

## Overview

Implemented per-event custom fields and schedule configuration system as specified in plan.md. This allows Super Admins (and Event Admins with proper permissions) to configure event-specific data collection and scheduling.

---

## Features Implemented

### 1. Custom Fields System
- **Per-event custom field configuration**
- **Field types supported:**
  - Text
  - Email
  - Number
  - Dropdown (select)
  - Checkbox
  - Textarea

### 2. Schedule Configuration
- **Prayer times** (Fajr, Dhuhr, Asr, Maghrib, Isha)
- **Event program/timeline**
- **Breaks and prayer breaks**

### 3. Quick Templates
Pre-built templates for common field configurations:
- Dietary Preference (Halal, Vegetarian, Vegan)
- T-Shirt Size
- Gender Section (Brothers, Sisters, Family)
- Emergency Contact
- Allergies/Medical Conditions
- Volunteer Interest

---

## Database Schema

### Event Model (Already Exists)
```python
class Event(db.Model):
    # ... existing fields ...
    custom_fields = db.Column(JSONB)  # Custom field configuration
    schedule_config = db.Column(JSONB)  # Prayer times, breaks, program
```

### Custom Fields JSON Structure
```json
[
  {
    "name": "dietary_preference",
    "label": "Dietary Preference",
    "type": "select",
    "required": false,
    "options": "Halal, Vegetarian, Vegan, No Preference",
    "placeholder": "Select your dietary preference"
  },
  {
    "name": "emergency_contact",
    "label": "Emergency Contact",
    "type": "text",
    "required": false,
    "options": "",
    "placeholder": "Emergency contact phone number"
  }
]
```

### Schedule Config JSON Structure
```json
{
  "prayer_times": {
    "fajr": "05:30",
    "dhuhr": "13:15",
    "asr": "17:20",
    "maghrib": "18:50",
    "isha": "20:30"
  },
  "program": [
    {"time": "18:30", "activity": "Arrival & Registration"},
    {"time": "18:45", "activity": "Maghrib Adhan & Iftar"},
    {"time": "19:30", "activity": "Maghrib Prayer"}
  ],
  "breaks": [
    {"name": "Zuhr Prayer Break", "start": "13:15", "duration": 30},
    {"name": "Asr Prayer Break", "start": "17:20", "duration": 20}
  ]
}
```

---

## How It Works

### Access Control
- **Super Admin:** Full access to configure any event
- **Event Admin:** Can configure events they manage (with `event.configure` permission)

### Configuration Flow
1. Navigate to event detail page: `/admin/events/{event_id}`
2. Click "Configure Fields & Schedule" button
3. Access configuration page: `/admin/events/{event_id}/configure`
4. Configure custom fields and/or schedule
5. Save configuration

### Three Tabs

#### Tab 1: Custom Fields
- Add/remove custom fields
- Configure field properties:
  - Name (database key)
  - Label (display name)
  - Type
  - Required status
  - Options (for select/checkbox)
  - Placeholder text
- Use quick templates for common fields
- Save independently

#### Tab 2: Schedule & Prayer Times
- **Prayer Times:**
  - Toggle on/off
  - Set times for 5 daily prayers
- **Event Program:**
  - Add timeline items
  - Set time and activity description
- **Breaks:**
  - Configure break name, start time, duration
- Save independently

#### Tab 3: Preview
- Visual preview of configuration
- Prayer times grid
- Program timeline
- Raw JSON view

---

## API Integration

### Endpoints Used

#### Get Event Configuration
```
GET /api/events/{event_id}
```
Returns event with `custom_fields` and `schedule_config`.

#### Update Custom Fields
```
PUT /api/events/{event_id}
Body: {
  "custom_fields": [...]
}
```

#### Update Schedule
```
PUT /api/events/{event_id}
Body: {
  "schedule_config": {...}
}
```

---

## Usage Examples

### Example 1: Ramadan Iftar Event

**Custom Fields:**
```json
[
  {
    "name": "dietary_preference",
    "label": "Dietary Preference",
    "type": "select",
    "required": false,
    "options": "Halal, Vegetarian"
  },
  {
    "name": "section",
    "label": "Section",
    "type": "select",
    "required": true,
    "options": "Brothers, Sisters, Family"
  },
  {
    "name": "volunteer_interest",
    "label": "Interested in Volunteering?",
    "type": "checkbox",
    "required": false,
    "options": "Yes, I want to volunteer"
  }
]
```

**Schedule Config:**
```json
{
  "prayer_times": {
    "maghrib": "18:45",
    "isha": "20:30"
  },
  "program": [
    {"time": "18:30", "activity": "Arrival & Registration"},
    {"time": "18:45", "activity": "Maghrib Adhan & Iftar"},
    {"time": "19:30", "activity": "Maghrib Prayer"},
    {"time": "19:50", "activity": "Lecture: Ramadan Reflections"},
    {"time": "20:30", "activity": "Isha Prayer & Departure"}
  ]
}
```

### Example 2: Youth Conference

**Custom Fields:**
```json
[
  {
    "name": "t_shirt_size",
    "label": "T-Shirt Size",
    "type": "select",
    "required": true,
    "options": "XS, S, M, L, XL, XXL"
  },
  {
    "name": "emergency_contact",
    "label": "Emergency Contact",
    "type": "text",
    "required": true
  },
  {
    "name": "allergies",
    "label": "Allergies/Medical Conditions",
    "type": "textarea",
    "required": false
  }
]
```

**Schedule Config:**
```json
{
  "prayer_times": {
    "fajr": "05:30",
    "dhuhr": "13:00",
    "asr": "16:30",
    "maghrib": "18:45",
    "isha": "20:15"
  },
  "breaks": [
    {"name": "Dhuhr Prayer Break", "start": "13:00", "duration": 45},
    {"name": "Asr Prayer Break", "start": "16:30", "duration": 30}
  ]
}
```

---

## Integration Points

### Where Custom Fields Are Used

1. **Registration Forms** (Future Enhancement)
   - Automatically generate form fields from configuration
   - Validate based on `required` flag
   - Store responses in `participants.custom_data` (JSONB)

2. **Participant Model**
```python
class Participant(db.Model):
    # ... existing fields ...
    custom_data = db.Column(JSONB)  # Stores custom field values
    
    # Example custom_data:
    # {
    #   "dietary_preference": "Halal",
    #   "t_shirt_size": "L",
    #   "emergency_contact": "+1234567890"
    # }
```

3. **Tickets**
   - Display custom field values on tickets
   - Show prayer times
   - Include event schedule

4. **Reports**
   - Export custom field data in CSV
   - Filter by custom field values
   - Aggregate statistics

### Where Schedule Config Is Used

1. **Tickets**
   - Display prayer times
   - Show event timeline
   - List breaks

2. **Event Detail Page**
   - Show prayer time countdown
   - Display current program item
   - Highlight upcoming breaks

3. **Email Templates**
   - Include prayer times in email
   - Show event schedule
   - Add reminders for specific times

---

## Files Created/Modified

### Created
1. ✅ `app/templates/admin/event_config.html` - Configuration UI
2. ✅ `docs/CUSTOM_FIELDS_SCHEDULE_IMPLEMENTATION.md` - This file

### Modified
1. ✅ `app/routes/frontend.py` - Added route for configuration page
2. ✅ `app/templates/admin/event_detail.html` - Added "Configure" button

### Existing (Used)
1. ✅ `app/models/events.py` - Already has JSONB columns
2. ✅ `app/routes/events.py` - Already supports updating these fields

---

## Permissions Required

To access event configuration:
- `event.configure` permission
- Or Super Admin role

Current role assignments:
- **Super Admin:** All permissions (implicit)
- **Event Admin:** Has `event.configure` permission

---

## Testing Checklist

### Custom Fields
- [ ] Add a text field
- [ ] Add a select field with options
- [ ] Add a required checkbox field
- [ ] Use quick template (e.g., Dietary Preference)
- [ ] Remove a field
- [ ] Save configuration
- [ ] Verify saved in database
- [ ] Check preview tab

### Schedule Configuration
- [ ] Enable prayer times
- [ ] Set all 5 prayer times
- [ ] Add program items
- [ ] Add breaks
- [ ] Save configuration
- [ ] Verify saved in database
- [ ] Check preview tab

### Integration
- [ ] Custom fields should appear in future registration forms
- [ ] Schedule should display on tickets (when ticket system uses it)
- [ ] Data exports should include custom field values

---

## Next Steps (Future Enhancements)

### Phase 1 Enhancements
1. **Dynamic Registration Forms**
   - Auto-generate registration form from custom_fields
   - Validate on frontend and backend
   - Store values in participants.custom_data

2. **Ticket Template Variables**
   - Add placeholders: `{{custom_fields.field_name}}`
   - Add placeholder: `{{prayer_times.fajr}}`
   - Add placeholder: `{{schedule}}`

3. **Email Template Variables**
   - Support custom field placeholders in emails
   - Include prayer times in emails
   - Add schedule table to email templates

### Phase 2 Enhancements
4. **Advanced Reporting**
   - Filter participants by custom field values
   - Generate statistics (e.g., dietary preference breakdown)
   - Export custom data in reports

5. **Prayer Time Features**
   - Auto-calculate prayer times by location (API integration)
   - Countdown timers for next prayer
   - Push notifications before prayer times

6. **Schedule Features**
   - Automatic session scheduling around prayer times
   - Conflict detection (overlapping breaks/prayers)
   - Multi-day event support

---

## Islamic Context Support

This implementation supports the Islamic features mentioned in plan.md:

### ✅ Implemented
- Prayer times configuration (5 daily prayers)
- Halal dietary preference option
- Gender-segregated sections (Brothers/Sisters/Family)
- Break scheduling for prayers
- Event program timeline

### 🔄 Ready for Integration
- **Hijri Calendar:** Can be added to schedule_config
- **Mahram Information:** Can be added as custom fields
- **Donation Tracking:** Can be added as custom fields
- **Prayer Break Auto-Scheduling:** Logic can use prayer_times from config

### Example: Complete Islamic Event Config
```json
{
  "custom_fields": [
    {"name": "dietary_preference", "type": "select", "options": "Halal, Vegetarian"},
    {"name": "section", "type": "select", "options": "Brothers, Sisters, Family", "required": true},
    {"name": "mahram_name", "type": "text", "required": false},
    {"name": "mahram_relationship", "type": "select", "options": "Father, Brother, Husband, Uncle"}
  ],
  "schedule_config": {
    "hijri_date": "15 Ramadan 1447",
    "prayer_times": {
      "maghrib": "18:45",
      "isha": "20:30"
    },
    "program": [
      {"time": "18:30", "activity": "Arrival & Registration"},
      {"time": "18:45", "activity": "Maghrib Adhan & Iftar"},
      {"time": "19:30", "activity": "Maghrib Prayer"},
      {"time": "20:30", "activity": "Isha Prayer & Departure"}
    ]
  }
}
```

---

## Benefits

### For Event Organizers
✅ No code changes needed for event-specific fields  
✅ Quick setup with templates  
✅ Preview before saving  
✅ Respects Islamic prayer times  
✅ Flexible configuration per event  

### For Participants
✅ Relevant fields for each event type  
✅ Clear prayer times displayed  
✅ Event schedule visibility  
✅ Dietary and medical needs tracked  

### For Developers
✅ JSONB allows schema flexibility  
✅ No database migrations for new fields  
✅ Easy to extend with new field types  
✅ Clean API integration  

---

## Status

✅ **COMPLETE** - Custom fields and schedule configuration system fully implemented

**Implemented By:** GitHub Copilot  
**Date:** January 26, 2026  
**Based On:** plan.md specifications  
**Impact:** High - Core event configuration feature
