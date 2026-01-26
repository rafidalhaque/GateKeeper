# Quick Start: Token Designer & CSS Guide

## Access the New Features

### Token Designer
**URL:** `/admin/token-designer`  
**Or:** Settings → Token Designer button

### CSS Guide
**URL:** `/admin/css-guide`  
**Or:** Click "CSS Guide" from any designer page

---

## Token Designer Quick Start

### 1. Select Event
Choose from dropdown → Loads existing template (if any)

### 2. Choose Template (Optional)
Click "Load Template" → Pick from 3 presets:
- **Default Badge** - Gradient with QR
- **Minimal White** - Clean and simple
- **Modern Dark** - Sleek with accent color

### 3. Edit & Preview
- Type HTML with `<style>` tags
- Preview updates automatically
- Use real participant data

### 4. Save
Click "Save Template" → Stored in database

---

## Common Badge Sizes

```css
@page { size: 3.5in 2in; }  /* Standard badge */
@page { size: 4in 3in; }    /* Jumbo badge */
@page { size: 4in 6in; }    /* Lanyard badge */
@page { size: 10in 1in; }   /* Wristband */
```

---

## Placeholders

```html
{{ event_name }}
{{ participant_name }}
{{ email }}
{{ team_name }}
{{ qr_code }}
{{ custom_fields.dietary_preference }}
```

---

## Quick Badge Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        @page { size: 3.5in 2in; margin: 0; }
        body { margin: 0; font-family: Arial; }
        .badge {
            width: 3.5in;
            height: 2in;
            padding: 15px;
            text-align: center;
            border: 2px solid #000;
        }
        h1 { font-size: 18px; margin: 10px 0; }
        .name { font-size: 22px; font-weight: bold; }
        img { width: 60px; }
    </style>
</head>
<body>
    <div class="badge">
        <h1>{{ event_name }}</h1>
        <div class="name">{{ participant_name }}</div>
        {% if team_name %}<p>{{ team_name }}</p>{% endif %}
        <img src="{{ qr_code }}">
    </div>
</body>
</html>
```

---

## CSS Guide Sections

1. **Page Setup** - Sizes, margins, orientation
2. **Layout** - Flexbox, centering, columns
3. **Typography** - Fonts, sizes, alignment
4. **Colors** - Hex, RGB, gradients
5. **Spacing** - Padding, margin
6. **Borders** - Styles, shadows, rounded corners
7. **Badge Sizes** - Common dimensions table
8. **Email** - Special rules for email templates

---

## Tips

✅ **Do:**
- Use inline CSS or `<style>` tags
- Test with real participant data
- Start with a template
- Reference CSS Guide

❌ **Don't:**
- Use external stylesheets
- Use JavaScript
- Forget units (px, mm, in)

---

## Need Help?

1. Open CSS Guide (link in designer)
2. Check examples section
3. Use template library
4. Test preview before saving

---

**Happy Designing!** 🎨
