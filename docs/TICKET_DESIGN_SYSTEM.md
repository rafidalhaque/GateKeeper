# Ticket Design System Documentation

## Overview

The Ticket Design System allows administrators to create custom ticket templates using HTML and CSS, with live preview and PDF generation capabilities.

## Features

✅ **Live HTML/CSS Editor** - Edit ticket templates in real-time
✅ **Live Preview** - See changes instantly before saving
✅ **Template Library** - Pre-built templates (Default, Minimal, Colorful)
✅ **Event-Specific Templates** - Each event can have its own ticket design
✅ **PDF Preview** - Download and test PDF output
✅ **Placeholder System** - Dynamic data injection using Jinja2 syntax
✅ **Responsive Interface** - Works on desktop and tablets

## Accessing the Ticket Designer

Navigate to: **Admin Panel → Ticket Designer**

Or directly: `http://localhost:5000/admin/ticket-designer`

## Available Placeholders

Use these placeholders in your HTML template to inject dynamic data:

| Placeholder | Description | Example Output |
|------------|-------------|----------------|
| `{{ event_name }}` | Event name | "Annual Tech Conference" |
| `{{ event_date }}` | Event date | "2026-01-25" |
| `{{ venue }}` | Event venue | "Convention Center" |
| `{{ participant_name }}` | Participant's name | "John Doe" |
| `{{ email }}` | Participant's email | "john@example.com" |
| `{{ participant_uuid }}` | Unique participant ID | "123e4567-e89b..." |
| `{{ team_name }}` | Team name (if team mode) | "Team Alpha" |
| `{{ team_id }}` | Team ID (if team mode) | "42" |
| `{{ t_shirt_size }}` | T-shirt size | "L" |
| `{{ qr_code }}` | QR code image (base64) | `data:image/png;base64,...` |
| `{{ custom_fields.field_name }}` | Custom field value | Varies by event |
| `{{ schedule }}` | Event schedule JSON | Prayer times, breaks, etc. |

### Conditional Placeholders

Use Jinja2 conditionals for optional fields:

```html
{% if team_name %}
<p><strong>Team:</strong> {{ team_name }} (ID: {{ team_id }})</p>
{% endif %}

{% if t_shirt_size %}
<p><strong>T-Shirt:</strong> {{ t_shirt_size }}</p>
{% endif %}

{% if custom_fields %}
<p><strong>Special Requirements:</strong> {{ custom_fields.dietary_preference }}</p>
{% endif %}
```

## Workflow

1. **Select Event** - Choose the event you want to design tickets for
2. **Edit HTML** - Modify the HTML template with your design
3. **Edit CSS** - Add custom styles
4. **Preview** - Click "Preview" to see live rendering
5. **Test PDF** - Download PDF to verify print layout
6. **Save** - Save template to the event

## Template Structure

### Basic Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* Your base styles */
    </style>
    {{ custom_css }}  <!-- This injects the CSS editor content -->
</head>
<body>
    <div class="ticket">
        <!-- Your ticket content -->
    </div>
</body>
</html>
```

### CSS Best Practices

```css
/* Page setup for PDF */
@page {
    size: A4;
    margin: 1cm;
}

/* Main ticket container */
.ticket {
    border: 2px solid #333;
    padding: 20px;
    max-width: 600px;
    margin: 0 auto;
}

/* QR code styling */
.qr-code {
    text-align: center;
    margin: 20px 0;
}

.qr-code img {
    max-width: 200px;
}
```

## API Endpoints

### Preview Ticket (HTML)

```
POST /api/tickets/preview
```

**Request Body:**
```json
{
    "event_id": "uuid",
    "participant_id": "uuid",  // Optional
    "html_template": "<html>...</html>",
    "css_template": "body { ... }"
}
```

**Response:**
```json
{
    "success": true,
    "html": "<html>rendered content</html>"
}
```

### Preview Ticket (PDF)

```
POST /api/tickets/preview-pdf
```

**Request Body:** Same as preview

**Response:** PDF file download

### Save Template

```
PUT /api/events/{event_id}
```

**Request Body:**
```json
{
    "ticket_template_html": "<html>...</html>",
    "ticket_template_css": "body { ... }"
}
```

## Pre-built Templates

### 1. Default Template
Clean and professional design with clear sections and QR code placement.

**Features:**
- Event header with venue
- Participant information section
- Team details (if applicable)
- Centered QR code
- Print-friendly layout

### 2. Minimal Template
Simplistic design with essential information only.

**Features:**
- Compact layout
- Minimalist styling
- Small QR code
- Fast rendering

### 3. Colorful Template
Vibrant design with gradients and modern styling.

**Features:**
- Gradient headers
- Rounded corners
- Shadow effects
- Eye-catching design
- Color-coded sections

## Tips & Tricks

### 1. Testing with Real Data

Always select a real participant when previewing to see actual data rendering.

### 2. Print Optimization

Use these CSS properties for better PDF output:

```css
@page {
    size: A4;
    margin: 1cm;
}

body {
    font-size: 12pt;  /* Use pt for print */
}

/* Avoid page breaks inside elements */
.ticket {
    page-break-inside: avoid;
}
```

### 3. QR Code Positioning

Center the QR code for easy scanning:

```css
.qr-section {
    text-align: center;
    padding: 20px;
    background: #f5f5f5;
}

.qr-section img {
    max-width: 200px;
    border: 2px solid #333;
    padding: 10px;
    background: white;
}
```

### 4. Responsive Design

While tickets are primarily for print, ensure they look good on screens too:

```css
@media screen {
    .ticket {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
}

@media print {
    .ticket {
        box-shadow: none;
    }
}
```

### 5. Custom Branding

Add your organization's logo:

```html
<div class="header">
    <img src="data:image/png;base64,..." alt="Logo" class="logo">
    <h1>{{ event_name }}</h1>
</div>
```

## Permissions Required

- **ticket.create** - Required to access the ticket designer
- **ticket.read** - Required to preview tickets
- **event.update** - Required to save templates to events

## Troubleshooting

### Preview Not Showing

**Issue:** Preview stays blank after clicking "Preview"
**Solution:** 
- Check browser console for errors
- Ensure an event is selected
- Verify HTML syntax is valid

### PDF Generation Fails

**Issue:** PDF download fails or shows errors
**Solution:**
- Check CSS for unsupported properties
- Verify QR code placeholder is present
- Ensure HTML is well-formed

### Template Not Saving

**Issue:** Save button doesn't work
**Solution:**
- Verify you have event.update permission
- Check that an event is selected
- Look for validation errors in console

### Placeholders Not Rendering

**Issue:** `{{ participant_name }}` shows as literal text
**Solution:**
- Ensure you're using double curly braces: `{{ }}`
- Check spelling of placeholder names
- Select a participant for preview

## Advanced Features

### Custom Fields Integration

Access event-specific custom fields:

```html
{% if custom_fields %}
    <div class="custom-section">
        <h3>Additional Information</h3>
        <p>Dietary: {{ custom_fields.dietary_preference }}</p>
        <p>Emergency: {{ custom_fields.emergency_contact }}</p>
    </div>
{% endif %}
```

### Schedule Display

Show prayer times or event schedule:

```html
{% if schedule %}
    <div class="schedule">
        <h3>Prayer Times</h3>
        <ul>
            <li>Fajr: {{ schedule.fajr }}</li>
            <li>Dhuhr: {{ schedule.dhuhr }}</li>
            <li>Asr: {{ schedule.asr }}</li>
        </ul>
    </div>
{% endif %}
```

### Multiple QR Codes

Add backup QR codes:

```html
<div class="qr-primary">
    <img src="{{ qr_code }}" alt="Primary QR">
</div>
<div class="qr-backup">
    <p>Backup URL: {{ participant_uuid }}</p>
</div>
```

## Best Practices

1. **Keep It Simple** - Don't overcomplicate the design
2. **Test on Real Data** - Always preview with actual participants
3. **Print Test** - Download PDF and print to verify
4. **Use Web-Safe Fonts** - Avoid exotic fonts that may not render in PDF
5. **Optimize File Size** - Large templates slow down generation
6. **Version Control** - Keep backups of working templates
7. **Document Custom CSS** - Comment your CSS for future reference

## Support

For issues or feature requests, please refer to:
- GitHub Issues: [Project Repository]
- Documentation: `/docs/plan.md`
- API Docs: `/api/docs`

## Future Enhancements

- [ ] Template versioning and history
- [ ] Import/export templates
- [ ] Template marketplace
- [ ] Drag-and-drop designer
- [ ] Multi-language support
- [ ] Batch ticket generation UI
- [ ] Email preview integration

---

**Last Updated:** January 25, 2026
**Version:** 1.0.0
