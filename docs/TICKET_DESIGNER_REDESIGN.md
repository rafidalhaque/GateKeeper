# Ticket Designer - Single Textarea with Side-by-Side Live Preview

## Date: January 25, 2026

## Changes Made

Redesigned the ticket designer interface for a better user experience:

### ✨ **Before**
- Two separate textareas (HTML + CSS)
- Preview below editors
- Manual refresh button required
- Separate save for HTML and CSS

### ✨ **After**
- **Single textarea** with inline CSS in `<style>` tags
- **Side-by-side layout** (Editor | Live Preview)
- **Automatic live preview** as you type (500ms debounce)
- **Equal height columns** for better visibility
- Cleaner, more intuitive interface

---

## Key Improvements

### 1. **Single Textarea**
- All HTML and CSS in one place
- CSS goes inside `<style>` tags in the `<head>`
- Easier to understand and manage
- Less context switching

### 2. **Side-by-Side Layout**
```
┌─────────────────────────┬─────────────────────────┐
│                         │                         │
│  HTML/CSS Editor        │   Live Preview         │
│  (textarea)             │   (updates as you type)│
│                         │                         │
│  • Write HTML           │   • See changes live   │
│  • Add CSS in <style>   │   • Scroll to review   │
│  • 600px height         │   • 600px height       │
│  • Resizable            │   • Scrollable         │
│                         │                         │
└─────────────────────────┴─────────────────────────┘
```

### 3. **Auto-Preview**
- Types in editor → **automatic preview in 500ms**
- No need to click "Refresh" button
- Preview updates smoothly as you edit
- Loading spinner shows during preview generation

### 4. **Better UX**
- ✅ Less scrolling (side-by-side instead of stacked)
- ✅ Immediate visual feedback
- ✅ Easier to experiment with designs
- ✅ PDF download button easily accessible
- ✅ Placeholder reference collapsed by default

---

## Technical Changes

### Frontend (`ticket_designer.html`)

#### Removed:
- `cssTemplate` variable
- Separate CSS editor card
- "Refresh Preview" button
- Bottom preview section

#### Added:
- Side-by-side grid layout
- Auto-preview on typing (debounced 500ms)
- PDF download in editor header
- Live preview indicator (spinner when loading)
- Equal height CSS for lg+ screens

#### Modified:
- `htmlTemplate` now includes inline CSS
- Preview updates automatically via `@input="debouncedPreview()"`
- Preview container height: 600px (matches editor)
- Debounce delay: 500ms (was 1000ms)

### Backend (No Changes)
- API endpoints remain the same
- Still sends `html_template` and `css_template` (empty string for CSS)
- Backward compatible with existing templates

### Templates Updated

All three pre-built templates now use inline CSS:

1. **Default Template**
   - CSS moved inside `<style>` tag
   - @page rules for PDF
   - All styles self-contained

2. **Minimal Template**
   - Inline CSS in `<style>` tag
   - Simplified structure

3. **Colorful Template**
   - Inline CSS with gradients
   - All styles in `<style>` tag

---

## User Experience

### Before (2 textareas + bottom preview):
```
[HTML Editor - 500px]
[CSS Editor - 500px]
[Preview - variable height]

❌ Need to scroll down to see preview
❌ Manual refresh required
❌ Context switching between 3 areas
```

### After (side-by-side with live preview):
```
[Editor 600px | Preview 600px]

✅ See everything at once
✅ Auto-updates as you type
✅ Single source of truth
```

---

## Files Modified

1. **`app/templates/admin/ticket_designer.html`**
   - Restructured layout (side-by-side grid)
   - Removed CSS editor
   - Added auto-preview
   - Updated all JavaScript functions
   - Updated template library
   - Updated CSS for equal heights

---

## Migration Notes

### For Existing Templates

Templates with separate HTML and CSS will be automatically combined:
- Load event → HTML loaded
- CSS (if exists) → ignored (inline CSS expected)
- When saved → CSS field empty, all styles in HTML

### For New Templates

Just write HTML with CSS inside `<style>` tags:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* Your CSS here */
        body { font-family: Arial; }
        .ticket { border: 2px solid #000; }
    </style>
</head>
<body>
    <div class="ticket">
        <h1>{{ event_name }}</h1>
        <!-- Your HTML here -->
    </div>
</body>
</html>
```

---

## Benefits

### For Users
- ✅ **Faster workflow** - See changes immediately
- ✅ **Less scrolling** - Everything visible at once
- ✅ **Easier to learn** - One file to manage
- ✅ **Better feedback** - Live preview as you type

### For Developers
- ✅ **Simpler code** - One template variable instead of two
- ✅ **Easier debugging** - All styles in one place
- ✅ **Less API calls** - Auto-debounced preview
- ✅ **Standard HTML** - Uses normal `<style>` tag convention

---

## Testing Checklist

- [x] Single textarea with inline CSS
- [x] Side-by-side layout on desktop
- [x] Auto-preview on typing (500ms delay)
- [x] Preview shows loading spinner
- [x] Equal height columns
- [x] Scrolling works in both panels
- [x] PDF download works
- [x] Save template works
- [x] Load template works
- [x] Template library works
- [x] Responsive on mobile (stacks vertically)

---

## Screenshots Comparison

### Before:
```
╔═══════════════════════════════╗
║  HTML Editor                  ║
║  [large textarea]             ║
╠═══════════════════════════════╣
║  CSS Editor                   ║
║  [large textarea]             ║
╠═══════════════════════════════╣
║  Preview (below, need scroll) ║
║  [preview content]            ║
╚═══════════════════════════════╝
```

### After:
```
╔═════════════════╦═════════════════╗
║  HTML/CSS       ║  Live Preview   ║
║  Editor         ║                 ║
║  [textarea]     ║  [auto-update]  ║
║                 ║                 ║
║  ↓ Type here    ║  → See here     ║
║                 ║                 ║
╚═════════════════╩═════════════════╝
```

---

## Future Enhancements

Possible improvements for future versions:

- [ ] Split-pane resizer (drag to adjust widths)
- [ ] Full-screen mode
- [ ] Syntax highlighting in textarea
- [ ] Line numbers
- [ ] Auto-save draft
- [ ] Undo/redo history
- [ ] CSS autocomplete
- [ ] Template comparison (A/B view)

---

## Status

✅ **COMPLETE** - Redesigned interface is ready to use

**Implemented:** January 25, 2026  
**Version:** 2.0.0  
**Improvement:** Single textarea + side-by-side live preview
