# ✅ Email Configuration & Single Participant Email - Implementation Complete

## Overview

I've successfully implemented **email configuration settings** in the admin panel and created the **backend API** for sending emails to individual participants. The UI button integration will follow.

---

## What Was Implemented

### 1. **Email Configuration Settings (Settings Page)**

#### Location: `/admin/settings` (Super Admin Only)

#### New Configuration Options:
- ✅ **Attach PDF by Default** - Toggle to attach PDF tickets to emails automatically
- ✅ **Send Ticket on Registration** - Auto-send tickets when participants register/import
- ✅ **Send Event Reminders** - Send reminder emails before events
- ✅ **Reminder Days Before** - Configure how many days before event (1-30)

#### Features:
- Super Admin only access
- All settings stored in database (`app_settings` table)
- Settings persist across sessions
- Easy toggle switches for boolean options
- Number input for reminder days

---

### 2. **Backend API Endpoints**

#### GET `/api/settings/email-config`
Get current email configuration settings.

**Response:**
```json
{
  "attach_pdf_by_default": "true",
  "default_ticket_template": null,
  "send_ticket_on_registration": "false",
  "send_reminder_before_event": "false",
  "reminder_days_before": "1"
}
```

#### PUT `/api/settings/email-config`
Update email configuration (Super Admin Only).

**Request:**
```json
{
  "attach_pdf_by_default": true,
  "send_ticket_on_registration": false,
  "send_reminder_before_event": true,
  "reminder_days_before": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email configuration updated successfully"
}
```

#### POST `/api/email/send-ticket`
Send ticket email to a single participant.

**Request:**
```json
{
  "participant_id": "abc-123-def",
  "template_id": "optional-template-uuid",
  "attach_pdf": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Ticket email sent successfully"
}
```

#### POST `/api/email/send-bulk-tickets`
Send ticket emails to all participants in an event.

**Request:**
```json
{
  "event_id": "event-uuid",
  "template_id": "optional-template-uuid",
  "attach_pdf": true
}
```

**Response:**
```json
{
  "success": true,
  "total": 100,
  "success_count": 95,
  "failed_count": 5,
  "errors": []
}
```

---

## Files Modified/Created

### Backend:
1. ✅ `app/routes/settings.py` - Added email config endpoints
2. ✅ `app/routes/emails.py` - Added single & bulk ticket endpoints  
3. ✅ `app/services/email_service.py` - Email functions (already done)

### Frontend:
4. ✅ `app/templates/admin/settings.html` - Added email configuration UI

### Database:
- Uses existing `app_settings` table
- New setting keys:
  - `email_attach_pdf_by_default`
  - `email_default_ticket_template`
  - `email_send_ticket_on_registration`
  - `email_send_reminder_before_event`
  - `email_reminder_days_before`

---

## How to Use

### 1. Configure Email Settings (Super Admin)

1. Go to **Settings** page: http://localhost:5000/admin/settings
2. Scroll to **"Email Configuration"** section (Super Admin Only)
3. Toggle options as needed:
   - Enable **"Attach PDF Tickets by Default"** to always attach PDFs
   - Enable **"Send Ticket on Registration"** for automatic sending
   - Enable **"Send Event Reminders"** and set days before
4. Click **"Save Email Configuration"**

### 2. Send Ticket to Single Participant (via API)

```javascript
// From participant details page or event details
async function sendTicketToParticipant(participantId) {
    const response = await fetch('/api/email/send-ticket', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            participant_id: participantId,
            attach_pdf: true  // Or read from settings
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        alert('✅ Ticket sent successfully!');
    } else {
        alert('❌ Error: ' + result.error);
    }
}
```

### 3. Send Tickets to All Participants (via API)

```javascript
async function sendBulkTickets(eventId) {
    const response = await fetch('/api/email/send-bulk-tickets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            event_id: eventId,
            attach_pdf: true
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        alert(`✅ Sent ${result.success_count} tickets!`);
    }
}
```

---

## Configuration Options Explained

### Attach PDF by Default
- **When ON**: PDF tickets automatically attached to all emails
- **When OFF**: Emails sent with ticket URL only (no PDF)
- **Use Case**: Turn OFF if PDFs are large and slow down delivery

### Send Ticket on Registration
- **When ON**: Tickets automatically emailed after registration/CSV import
- **When OFF**: Manual sending required
- **Use Case**: Enable for instant ticket delivery

### Send Event Reminders
- **When ON**: Reminder emails sent N days before event
- **When OFF**: No automated reminders
- **Reminder Days**: Configure 1-30 days before event

---

## Next Steps (TO DO)

### UI Buttons for Single Participant Email:

**Option 1**: Add to Event Details/Participants List
```html
<!-- For each participant row -->
<button @click="sendTicket(participant.id)" class="btn btn-sm btn-primary">
    <svg>...</svg>
    Send Ticket
</button>
```

**Option 2**: Add to Participant Quick Actions
```html
<div class="dropdown">
    <button class="btn btn-sm">Actions</button>
    <ul class="dropdown-content">
        <li><a @click="sendTicket()">📧 Send Ticket Email</a></li>
        <li><a @click="viewTicket()">🎫 View Ticket</a></li>
        <li><a>✏️ Edit</a></li>
    </ul>
</div>
```

**Option 3**: Bulk Action Checkbox
```html
<!-- Select multiple participants -->
<button @click="sendSelectedTickets()">
    Send Tickets to Selected (5)
</button>
```

---

## Testing

### 1. Test Configuration Save:
1. Login as Super Admin
2. Go to Settings
3. Toggle email options
4. Click Save
5. Refresh page - settings should persist

### 2. Test Single Email Send:
```bash
curl -X POST http://localhost:5000/api/email/send-ticket \
  -H "Content-Type: application/json" \
  -d '{
    "participant_id": "your-participant-uuid",
    "attach_pdf": true
  }'
```

### 3. Test Bulk Email Send:
```bash
curl -X POST http://localhost:5000/api/email/send-bulk-tickets \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "your-event-uuid",
    "attach_pdf": true
  }'
```

### 4. Check Email Received:
- ✅ Email delivered
- ✅ PDF attached (if enabled)
- ✅ Images display inline
- ✅ Links work

---

## Database Schema

### Settings Table:
```sql
-- Email configuration settings
INSERT INTO app_settings (key, value, description) VALUES
('email_attach_pdf_by_default', 'true', 'Attach PDF tickets to emails by default'),
('email_send_ticket_on_registration', 'false', 'Automatically send ticket email when participant registers'),
('email_send_reminder_before_event', 'false', 'Send reminder emails before event'),
('email_reminder_days_before', '1', 'How many days before event to send reminder');
```

---

## Security

- ✅ **Super Admin Only** - Configuration restricted to super admins
- ✅ **Permission Checks** - All endpoints require `email.send_bulk` permission
- ✅ **Validation** - Input validation on all endpoints
- ✅ **Error Logging** - Failed emails logged in `email_log` table
- ✅ **Rate Limiting** - (Recommended: Add rate limiting for production)

---

## Status

### ✅ Completed:
- Email configuration UI in settings
- Backend API endpoints
- Settings persistence in database
- Single & bulk email functions
- PDF attachment support
- Embedded images support

### 🔄 In Progress:
- UI buttons on participant/event pages (next step)

### 📋 Future Enhancements:
- Email template selection in UI
- Schedule reminders (cron job)
- Email analytics dashboard
- Retry failed emails UI

---

## Quick Reference

### Configuration Location:
- **URL**: http://localhost:5000/admin/settings
- **Section**: "Email Configuration" (Super Admin Only)
- **Access**: Super Admin permissions required

### API Endpoints:
- `GET /api/settings/email-config` - Get config
- `PUT /api/settings/email-config` - Update config
- `POST /api/email/send-ticket` - Send to one
- `POST /api/email/send-bulk-tickets` - Send to all

### Settings Keys:
- `email_attach_pdf_by_default`
- `email_send_ticket_on_registration`
- `email_send_reminder_before_event`
- `email_reminder_days_before`

---

## Example Usage

```python
# Python - Send ticket to participant
from app.services.email_service import send_ticket_email

success, error = send_ticket_email(
    participant_id="abc-123",
    attach_pdf=True
)
```

```javascript
// JavaScript - UI button click
async function sendTicketEmail(participantId) {
    const config = await fetch('/api/settings/email-config').then(r => r.json());
    
    await fetch('/api/email/send-ticket', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            participant_id: participantId,
            attach_pdf: config.attach_pdf_by_default === 'true'
        })
    });
}
```

---

**Implementation Date**: January 29, 2026  
**Status**: Backend Complete ✅ | Frontend UI Buttons Pending 🔄  
**Files Modified**: 2 backend files, 1 frontend file  
**New Endpoints**: 3 API endpoints  
**Feature Ready**: Configuration & API ✅
