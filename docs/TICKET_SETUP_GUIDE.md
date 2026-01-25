# Ticket Design System - Setup & Installation Guide

## Prerequisites

✅ GateKeeper application already installed
✅ PostgreSQL database configured
✅ WeasyPrint dependencies installed
✅ Admin user with appropriate permissions

---

## Installation Steps

### 1. Update Permissions

Run the permissions seeding command to add the new `ticket.create` permission:

```bash
flask --app run.py seed-permissions
```

Expected output:
```
Seeding permissions...
  Created permission: ticket.create
Permissions seeded successfully!
```

### 2. Update Role Assignments

If you already have Event Admin roles assigned, reseed roles to add the new permission:

```bash
flask --app run.py seed-roles
```

This will add `ticket.create` to existing Event Admin roles.

### 3. Verify Installation

1. **Check Navigation:**
   - Log in to admin panel
   - Look for "Ticket Designer" in the sidebar
   - Should appear between "Email Templates" and "Reports"

2. **Check Settings:**
   - Navigate to Admin → Settings
   - Look for "Quick Links" section at the top
   - Should have "Ticket Designer" button

3. **Test Access:**
   - Click on "Ticket Designer" link
   - Page should load without errors
   - Should see HTML/CSS editors and preview panel

### 4. Create Your First Ticket Template

1. **Select an Event:**
   - Use the event dropdown to select an event
   - If no events exist, create one first

2. **Choose a Template:**
   - Click "Load Template" button
   - Select from Default, Minimal, or Colorful
   - Or start from scratch

3. **Customize:**
   - Modify HTML in the left editor
   - Add custom CSS in the right editor
   - Use placeholders from the reference

4. **Preview:**
   - Click "Preview" to see live rendering
   - Select different participants to test with real data

5. **Test PDF:**
   - Click "Download PDF" to test print output
   - Verify QR code is scannable
   - Check layout on actual paper if needed

6. **Save:**
   - Click "Save Template"
   - Template is now saved to the event
   - Will be used for all ticket generation

---

## Troubleshooting

### Permission Denied Error

**Symptoms:** 403 Forbidden when accessing `/admin/ticket-designer`

**Solution:**
```bash
# Check your role has ticket.create permission
flask --app run.py seed-roles

# Or manually assign permission via admin UI
```

### WeasyPrint Errors

**Symptoms:** PDF generation fails with errors

**Solution:**
```bash
# Install/reinstall WeasyPrint dependencies
pip install --upgrade WeasyPrint

# On Windows, you may need GTK+
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
```

### Preview Shows Blank

**Symptoms:** Preview panel stays empty after clicking "Preview"

**Solution:**
1. Check browser console for JavaScript errors
2. Verify an event is selected
3. Check HTML syntax is valid
4. Try "Reset to Default" button

### Template Not Saving

**Symptoms:** Save button doesn't work or shows error

**Solution:**
1. Verify you have `event.update` permission
2. Check that an event is selected
3. Look for error messages in browser console
4. Verify database connection

### Placeholders Show as Text

**Symptoms:** `{{ participant_name }}` appears literally in preview

**Solution:**
- Ensure you're using double curly braces: `{{ }}`
- Check spelling of placeholder names
- Verify placeholder is in the available list

---

## Database Schema

The ticket design system uses existing Event table columns:

```sql
ALTER TABLE events ADD COLUMN IF NOT EXISTS ticket_template_html TEXT;
ALTER TABLE events ADD COLUMN IF NOT EXISTS ticket_template_css TEXT;
```

These columns should already exist from initial migration. If not:

```bash
flask --app run.py db upgrade
```

---

## Permissions Reference

### Required Permissions

| Action | Permission Required |
|--------|-------------------|
| Access ticket designer | `ticket.create` |
| Preview tickets | `ticket.create` |
| Download PDF preview | `ticket.create` |
| Save template to event | `event.update` |

### Role Defaults

| Role | Has Access |
|------|-----------|
| Super Admin | ✅ Yes (all permissions) |
| Event Admin | ✅ Yes (includes ticket.create) |
| Booth Manager | ❌ No (read-only) |

---

## Configuration

### Environment Variables

No additional environment variables required. Uses existing configuration:

- `SUPABASE_URL` - For authentication
- `SUPABASE_KEY` - For authentication
- `DATABASE_URL` - For storing templates

### WeasyPrint Configuration

WeasyPrint uses system fonts. For best results:

**Recommended Fonts:**
- Arial (default, widely available)
- Helvetica
- Times New Roman
- Courier

**Custom Fonts:**
```css
@font-face {
    font-family: 'CustomFont';
    src: url('path/to/font.ttf');
}

body {
    font-family: 'CustomFont', Arial, sans-serif;
}
```

---

## Testing

### Manual Testing Checklist

- [ ] Can access ticket designer page
- [ ] Can select an event
- [ ] Can load template from library
- [ ] Can edit HTML
- [ ] Can edit CSS
- [ ] Preview button works
- [ ] Preview shows correct data
- [ ] Download PDF works
- [ ] PDF is scannable (QR code works)
- [ ] Save template works
- [ ] Template persists after page reload
- [ ] Different participants show different data

### Automated Testing

```bash
# Run Python tests
pytest tests/test_ticket_service.py

# Test API endpoints
curl -X POST http://localhost:5000/api/tickets/preview \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event_id": "YOUR_EVENT_ID", "html_template": "<html>...</html>"}'
```

---

## Production Deployment

### Before Deploying

1. **Test Thoroughly:**
   - Test with real events and participants
   - Verify PDF generation works
   - Test QR codes are scannable
   - Check print quality

2. **Optimize:**
   - Consider PDF caching for frequently used templates
   - Set up CDN for static assets
   - Configure Redis for session storage

3. **Backup:**
   - Backup database before migration
   - Keep copy of default templates
   - Document any custom CSS/HTML

### Deployment Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
flask --app run.py db upgrade

# 4. Seed permissions
flask --app run.py seed-permissions

# 5. Reseed roles
flask --app run.py seed-roles

# 6. Restart application
systemctl restart gatekeeper  # or your process manager
```

### Post-Deployment

1. Verify ticket designer is accessible
2. Test ticket generation
3. Verify PDF downloads work
4. Test with real events
5. Monitor error logs

---

## Support & Documentation

- **Full Documentation:** `docs/TICKET_DESIGN_SYSTEM.md`
- **Quick Reference:** `docs/TICKET_QUICK_REFERENCE.md`
- **Implementation Details:** `docs/TICKET_DESIGN_IMPLEMENTATION.md`
- **API Documentation:** `/api/docs` (Swagger UI)
- **Project Plan:** `docs/plan.md` (Section 10)

---

## FAQ

**Q: Can I use the same template for multiple events?**  
A: Not directly. You need to copy/paste the HTML/CSS between events. Template sharing is planned for future versions.

**Q: What happens to existing tickets if I change the template?**  
A: Already generated PDFs remain unchanged. Only new tickets will use the new template.

**Q: Can I preview without saving?**  
A: Yes! Preview is completely separate from save. Test as much as you want.

**Q: How do I backup my templates?**  
A: Templates are stored in the database. Regular database backups will include templates. You can also copy/paste the HTML/CSS to a text file.

**Q: Can I use JavaScript in templates?**  
A: No. Templates are rendered server-side for PDF generation. Only HTML/CSS is supported.

**Q: What CSS properties work in PDF?**  
A: Most standard CSS works. WeasyPrint supports CSS 2.1 and some CSS3 features. Avoid: animations, transforms, advanced flexbox.

**Q: Can I embed images other than QR codes?**  
A: Yes, use base64-encoded images: `<img src="data:image/png;base64,...">` or absolute URLs.

**Q: How large can templates be?**  
A: No hard limit, but keep under 100KB for performance. Typical templates are 5-20KB.

---

**Setup Complete!** 🎉

You're now ready to design custom tickets. Start with the default template and customize from there.

For help, see `docs/TICKET_DESIGN_SYSTEM.md` or contact support.
