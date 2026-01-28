# 📧 Ticket Email with PDF Attachment - Implementation Complete

## Overview

I've successfully implemented the ability to **automatically attach PDF tickets to emails**. Now when you send ticket emails to participants, they will receive:

1. ✅ **Beautiful HTML Email** (using email templates)
2. ✅ **PDF Ticket Attachment** (ready to print or save)
3. ✅ **Embedded Images** (logos displayed inline using CID)

---

## What Was Implemented

### 1. **Enhanced Email Service**

**File**: `app/services/email_service.py`

#### New Features:
- ✅ **PDF Attachment Support** - Attach generated tickets to emails
- ✅ **Embedded Images (CID)** - Inline images in HTML emails
- ✅ **MIME Multipart** - Proper email structure for attachments
- ✅ **Template Integration** - Uses email templates with Jinja2

#### New Functions:

##### `send_ticket_email(participant_id, template_id=None, attach_pdf=True)`
Send ticket email to a single participant with PDF attachment.

**Parameters:**
- `participant_id`: Participant ID (required)
- `template_id`: Email template ID (optional, uses default "ticket" template)
- `attach_pdf`: Whether to attach PDF (default: True)

**Returns:**
```python
(success: bool, error_message: str or None)
```

**Example:**
```python
from app.services.email_service import send_ticket_email

# Send with PDF attachment
success, error = send_ticket_email(participant_id="abc-123")

# Send without PDF (URL only)
success, error = send_ticket_email(participant_id="abc-123", attach_pdf=False)

# Use specific template
success, error = send_ticket_email(
    participant_id="abc-123",
    template_id="template-uuid",
    attach_pdf=True
)
```

##### `send_bulk_ticket_emails(event_id, template_id=None, attach_pdf=True)`
Send ticket emails to ALL participants in an event.

**Parameters:**
- `event_id`: Event ID (required)
- `template_id`: Email template ID (optional)
- `attach_pdf`: Whether to attach PDFs (default: True)

**Returns:**
```python
{
    'success': True,
    'total': 100,
    'success_count': 95,
    'failed_count': 5,
    'errors': [...]
}
```

**Example:**
```python
from app.services.email_service import send_bulk_ticket_emails

# Send to all participants with PDFs
result = send_bulk_ticket_emails(event_id="event-uuid")

print(f"Sent {result['success_count']} tickets successfully")
```

### 2. **New API Endpoints**

**File**: `app/routes/emails.py`

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

### 3. **How It Works**

#### Email Structure:
```
📧 Email Message
├── 📝 Alternative (text/html choice)
│   ├── Plain Text Body
│   └── Related (HTML + images)
│       ├── HTML Content
│       └── 🖼️ Embedded Images (CID)
│           ├── logo.png (cid:img_abc@gatekeeper)
│           ├── banner.png (cid:img_def@gatekeeper)
│           └── ...
└── 📎 Attachments
    └── ticket_John_Doe.pdf
```

#### Flow Diagram:
```
1. Request to send ticket
   ↓
2. Load participant & event data
   ↓
3. Load email template (type='ticket')
   ↓
4. Render template with Jinja2
   ↓
5. Generate PDF ticket
   ↓
6. Extract CID references from HTML
   ↓
7. Load embedded images from database
   ↓
8. Build MIME multipart message
   ├── Add text/HTML
   ├── Add embedded images
   └── Add PDF attachment
   ↓
9. Send via SMTP
   ↓
10. Log email status
```

---

## Features

### ✅ **PDF Attachment**
- Ticket automatically generated and attached
- Filename: `ticket_Participant_Name.pdf`
- Ready to print or save
- Same design as ticket designer

### ✅ **Embedded Images (CID)**
- Logos and banners displayed inline
- No broken image links
- Works in all email clients
- Format: `<img src="cid:img_abc123@gatekeeper">`

### ✅ **Template Integration**
- Uses email templates from database
- Jinja2 variable support
- Conditional content (team info, etc.)
- Custom styling per template

### ✅ **Error Handling**
- Logs all email attempts
- Tracks failures with error messages
- Returns detailed error information
- Supports retry functionality

### ✅ **Flexible Options**
- Choose to attach PDF or not
- Select specific email template
- Send to individual or bulk
- Plain text fallback

---

## Usage Examples

### Example 1: Send Ticket to One Participant (Python)

```python
from app.services.email_service import send_ticket_email

# Send with default template and PDF
success, error = send_ticket_email("participant-uuid")

if success:
    print("✅ Ticket sent successfully!")
else:
    print(f"❌ Error: {error}")
```

### Example 2: Send Tickets to All Participants (Python)

```python
from app.services.email_service import send_bulk_ticket_emails

# Send to all participants in an event
result = send_bulk_ticket_emails("event-uuid", attach_pdf=True)

print(f"Total: {result['total']}")
print(f"Success: {result['success_count']}")
print(f"Failed: {result['failed_count']}")

# Check errors
for error in result['errors']:
    print(f"❌ {error['email']}: {error['error']}")
```

### Example 3: Send via API (curl)

```bash
# Send to single participant
curl -X POST http://localhost:5000/api/email/send-ticket \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "participant_id": "abc-123-def",
    "attach_pdf": true
  }'

# Send to all participants
curl -X POST http://localhost:5000/api/email/send-bulk-tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "event_id": "event-uuid",
    "attach_pdf": true
  }'
```

### Example 4: From Event Details Page (JavaScript)

```javascript
// Send tickets to all participants
async function sendAllTickets(eventId) {
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
    } else {
        alert(`❌ Error: ${result.error}`);
    }
}
```

---

## Email Template Variables

When creating ticket email templates, you have access to:

### Participant Variables:
```jinja2
{{ participant.name }}          # Full name
{{ participant.email }}         # Email address
{{ participant.unique_url }}    # Ticket URL (web view)
{{ participant.uuid }}          # Unique identifier
```

### Event Variables:
```jinja2
{{ event.name }}               # Event name
{{ event.date }}               # Event date (formatted)
{{ event.venue }}              # Venue location
{{ event.mode }}               # Solo/Team mode
```

### Team Variables (conditional):
```jinja2
{% if team %}
  {{ team.name }}              # Team name
  {{ team.id }}                # Team ID
{% endif %}
```

### System Variables:
```jinja2
{{ current_year }}             # 2026
{{ app_name }}                 # GateKeeper
{{ support_email }}            # support@example.com
```

### Custom Fields:
```jinja2
{% if custom_fields %}
  {{ custom_fields.t_shirt_size }}
  {{ custom_fields.dietary }}
  etc.
{% endif %}
```

---

## Example Email Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; background: #f9f9f9; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header with logo -->
        <div class="header">
            <img src="cid:img_abc123@gatekeeper" style="width: 100px; margin-bottom: 15px;" alt="Logo">
            <h1>Your Ticket is Ready!</h1>
            <p>{{ event.name }}</p>
        </div>
        
        <!-- Content -->
        <div class="content">
            <h2>Hello {{ participant.name }}! 👋</h2>
            
            <p>We're excited to have you at <strong>{{ event.name }}</strong>!</p>
            
            <p><strong>📅 Date:</strong> {{ event.date }}<br>
            <strong>📍 Venue:</strong> {{ event.venue }}</p>
            
            {% if team %}
            <p><strong>🤝 Team:</strong> {{ team.name }}</p>
            {% endif %}
            
            <p>Your ticket is attached to this email as a PDF. You can also view it online:</p>
            
            <p style="text-align: center;">
                <a href="{{ participant.unique_url }}" class="button">View Ticket Online</a>
            </p>
            
            <p><strong>Important:</strong> Please bring either the printed ticket or show the QR code on your phone at the entrance.</p>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>© {{ current_year }} {{ app_name }}. All rights reserved.</p>
            <p>Need help? Contact us at {{ support_email }}</p>
        </div>
    </div>
</body>
</html>
```

**Subject**: `Your Ticket for {{ event.name }} - {{ participant.name }}`

---

## Configuration

### Required Settings:

**SMTP Configuration** (already configured):
- Server, port, username, password
- Can be set in database (Settings → SMTP) or .env

**APP_URL** (for absolute URLs):
```bash
# .env
APP_URL=http://localhost:5000  # Development
# APP_URL=https://yourdomain.com  # Production
```

### Optional Settings:

**Default Email Template:**
- Type: "ticket"
- Created in Email Templates page
- Used when no template_id specified

---

## Testing

### 1. Create Email Template:
1. Go to **Email Templates** page
2. Click **"Create Template"**
3. Name: "Ticket Delivery"
4. Type: "Ticket"
5. Subject: `Your Ticket for {{ event.name }}`
6. HTML: Use example above
7. Save

### 2. Send Test Ticket:
```python
from app.services.email_service import send_ticket_email

# Get a participant ID (from database or event page)
success, error = send_ticket_email("participant-uuid")

if success:
    print("✅ Check your email!")
```

### 3. Check Email:
- ✅ Email received with HTML content
- ✅ Images display inline (logos, banners)
- ✅ PDF attachment present
- ✅ PDF opens correctly
- ✅ Ticket has QR code and details

---

## Common Use Cases

### Use Case 1: Send Tickets After Registration
```python
# After CSV import or manual registration
for participant in new_participants:
    send_ticket_email(participant.id)
```

### Use Case 2: Resend Lost Tickets
```python
# From participant details page
send_ticket_email(participant_id, attach_pdf=True)
```

### Use Case 3: Mass Send Before Event
```python
# 1 day before event, send reminders with tickets
send_bulk_ticket_emails(event_id)
```

### Use Case 4: Custom Template for VIPs
```python
# Use special VIP template
vip_template = EmailTemplate.query.filter_by(name="VIP Ticket").first()
send_ticket_email(vip_participant_id, template_id=vip_template.id)
```

---

## Troubleshooting

### Issue: PDF Not Attached
**Solution**: Check if PDF generation works:
```python
from app.services.ticket_service import generate_ticket_pdf
pdf = generate_ticket_pdf(participant_id)
if not pdf:
    print("❌ PDF generation failed")
```

### Issue: Images Not Showing
**Solution**: 
1. Check images uploaded in Image Library
2. Verify CID format: `cid:img_xxxxx@gatekeeper`
3. Ensure images are active

### Issue: Email Not Sending
**Solution**:
1. Check SMTP configuration (Settings → SMTP)
2. Test SMTP with "Send Test Email"
3. Check email logs: `/api/email/logs?event_id=xxx`

### Issue: Template Not Found
**Solution**:
1. Create a template with type="ticket"
2. Or specify template_id in function call

---

## Status

✅ **COMPLETE** - Ticket emails now include PDF attachments!

### What Works:
- ✅ PDF ticket attachment
- ✅ Embedded images (CID)
- ✅ Email template integration
- ✅ Single & bulk sending
- ✅ Error logging
- ✅ API endpoints
- ✅ Custom template support

### Next Steps:
1. Create your first ticket email template
2. Upload logos to Image Library
3. Test sending to yourself
4. Send to all participants!

---

**Implementation Date**: January 29, 2026  
**Files Modified**: 2 files  
**New Functions**: 2 functions  
**New Endpoints**: 2 endpoints  
**Feature Status**: Production Ready ✅

---

## Quick Start

```python
# 1. Import the function
from app.services.email_service import send_ticket_email

# 2. Send a ticket
success, error = send_ticket_email("participant-uuid")

# 3. Check result
if success:
    print("✅ Email sent with PDF attached!")
else:
    print(f"❌ Error: {error}")
```

**That's it!** Your participants will now receive beautiful emails with PDF tickets attached! 🎉📧🎫
