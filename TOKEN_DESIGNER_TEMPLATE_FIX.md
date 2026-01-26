# ✅ Fixed: Token Designer Template Error

**Date:** January 26, 2026  
**Issue:** 'custom_fields' is undefined error in token designer  
**Status:** RESOLVED ✅

---

## Problem

When accessing `/admin/token-designer`, the following error occurred:

```
[2026-01-26 11:43:53,471] ERROR in errors: Unhandled exception: 'custom_fields' is undefined
127.0.0.1 - - [26/Jan/2026 11:43:53] "GET /admin/token-designer HTTP/1.1" 500 -
```

**Root Cause:** In the token designer template, Jinja2 placeholders were shown in documentation without proper escaping. The template tried to evaluate `{{ custom_fields.field_name }}` as a Jinja2 variable instead of displaying it as literal text.

---

## Solution

### Fixed File
`app/templates/admin/token_designer.html`

### Change Made
Escaped all Jinja2 placeholders in the documentation section:

**Before:**
```html
<code>{{ participant_name }}</code>,
<code>{{ custom_fields.field_name }}</code>
```

**After:**
```html
<code>{{ "{{" }} participant_name }}</code>,
<code>{{ "{{" }} custom_fields.field_name }}</code>
```

### Technique Used
Used Jinja2's string concatenation to display literal `{{` characters:
- `{{ "{{" }}` renders as `{{`
- This prevents Jinja2 from trying to evaluate the variable

---

## Verification

✅ **Token designer loads without errors**  
✅ **Placeholders displayed correctly as documentation**  
✅ **No undefined variable errors**  
✅ **Ticket designer uses same technique (already correct)**  

---

## Affected Section

The fix was applied to the "Available Placeholders" documentation box that shows users what variables they can use in their templates.

**Location in template:** Lines 120-137

**Purpose:** Shows users available Jinja2 placeholders for token templates

**Fixed placeholders:**
- `{{ "{{" }} participant_name }}`
- `{{ "{{" }} email }}`
- `{{ "{{" }} participant_uuid }}`
- `{{ "{{" }} event_name }}`
- `{{ "{{" }} event_date }}`
- `{{ "{{" }} venue }}`
- `{{ "{{" }} qr_code }}`
- `{{ "{{" }} team_name }}`
- `{{ "{{" }} team_id }}`
- `{{ "{{" }} custom_fields.field_name }}`

---

## Why This Happened

When Jinja2 renders a template, it evaluates anything inside `{{ }}`. Since we wanted to *show* the literal text `{{ custom_fields.field_name }}` to users as documentation, we needed to escape it.

**Without escaping:** Jinja2 tries to find a variable called `custom_fields`  
**With escaping:** Jinja2 outputs the literal characters `{{ custom_fields.field_name }}`

---

## Similar Patterns

This same technique is used in:
- ✅ `ticket_designer.html` - Already properly escaped
- ✅ `token_designer.html` - Now fixed
- ✅ Template presets (JavaScript strings) - Don't need escaping

---

## Testing

To verify the fix:

1. Start Flask app: `flask --app run.py run`
2. Navigate to `/admin/token-designer`
3. Should load without errors ✅
4. Documentation box should show placeholders correctly ✅

---

## Status

**Before:** 500 Internal Server Error  
**After:** Page loads successfully ✅

**Token Designer:** Fully functional  
**Documentation:** Displays correctly  
**User Experience:** Professional and clear  

---

## Related Documentation

The placeholders shown in the documentation are for users to copy into their token templates. They work as follows:

**In user's token template:**
```html
<div class="name">{{ participant_name }}</div>
{% if custom_fields.dietary %}
  <p>Dietary: {{ custom_fields.dietary }}</p>
{% endif %}
```

**At render time:** These get replaced with actual participant data

**In our documentation:** We show them as literal examples using `{{ "{{" }}`

---

## Files Modified

1. ✅ `app/templates/admin/token_designer.html` - Fixed Jinja2 escaping

---

## Prevention

When showing Jinja2 syntax as documentation in Jinja2 templates:
- ✅ Use `{{ "{{" }}` for opening braces
- ✅ Use `{{ "}}" }}` for closing braces (if needed)
- ✅ Or use `{{ '{{' }}` with single quotes

---

**Issue:** RESOLVED ✅  
**Time to Fix:** ~5 minutes  
**Impact:** None (template only)  
**Data Loss:** None  

---

**Last Updated:** January 26, 2026  
**Status:** Fixed and Verified ✅
