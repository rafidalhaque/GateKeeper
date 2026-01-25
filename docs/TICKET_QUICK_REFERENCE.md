# Ticket Designer Quick Reference

## 🎨 Essential Placeholders

```html
<!-- Basic Info -->
{{ event_name }}
{{ event_date }}
{{ venue }}
{{ participant_name }}
{{ email }}

<!-- QR Code (Required) -->
<img src="{{ qr_code }}" alt="QR Code">

<!-- Conditional Fields -->
{% if team_name %}
  Team: {{ team_name }} (ID: {{ team_id }})
{% endif %}

{% if t_shirt_size %}
  Size: {{ t_shirt_size }}
{% endif %}
```

## 📐 PDF-Optimized CSS

```css
/* Page Setup */
@page {
    size: A4;
    margin: 1cm;
}

/* Typography */
body {
    font-family: Arial, sans-serif;
    font-size: 12pt; /* Use pt for print */
}

/* Container */
.ticket {
    max-width: 600px;
    margin: 0 auto;
    border: 2px solid #333;
    padding: 20px;
    page-break-inside: avoid; /* Prevent page breaks */
}

/* QR Code */
.qr-code {
    text-align: center;
    margin: 20px 0;
}

.qr-code img {
    max-width: 200px;
}
```

## ⚡ Quick Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {{ custom_css }}
</head>
<body>
    <div class="ticket">
        <h1>{{ event_name }}</h1>
        <p>{{ event_date }} • {{ venue }}</p>
        <hr>
        <p><strong>{{ participant_name }}</strong></p>
        <p>{{ email }}</p>
        {% if team_name %}
        <p>Team: {{ team_name }}</p>
        {% endif %}
        <div class="qr-code">
            <img src="{{ qr_code }}" alt="QR">
        </div>
    </div>
</body>
</html>
```

## 🔥 Pro Tips

1. **Always include** `{{ custom_css }}` in `<head>`
2. **Always include** QR code: `{{ qr_code }}`
3. **Use conditionals** for optional fields
4. **Test on real data** before saving
5. **Download PDF** to verify print layout
6. **Keep it simple** - complex layouts may fail in PDF

## 🎯 Common Use Cases

### Bordered Ticket
```css
.ticket {
    border: 3px solid #000;
    padding: 30px;
    border-radius: 10px;
}
```

### Gradient Header
```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    text-align: center;
}
```

### Two-Column Layout
```css
.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
```

### Centered Everything
```css
.ticket {
    text-align: center;
}
```

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Preview blank | Select an event first |
| PDF fails | Check CSS syntax |
| Placeholders show as text | Use `{{ }}` not `{ }` |
| QR not showing | Include `{{ qr_code }}` in `<img src>` |
| Fonts weird in PDF | Use web-safe fonts only |

## 📱 Access Points

- **Navigation:** Admin → Ticket Designer
- **Settings:** Quick Links → Ticket Designer
- **Direct URL:** `/admin/ticket-designer`

---

**Need Help?** See `docs/TICKET_DESIGN_SYSTEM.md` for full documentation.
