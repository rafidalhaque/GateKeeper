# Image Attachment System - Testing Checklist

> **✅ UPDATE (Jan 28, 2026)**: Path handling bug fixed! Upload functionality restored.  
> See: `docs/IMAGE_UPLOAD_PATH_FIX.md` for details.

## Before You Start
- [ ] Flask app is running: `flask --app run.py run`
- [ ] Database migrations applied: `flask --app run.py db upgrade`
- [ ] Upload directory exists: `uploads/attachments/`
- [ ] Logged in as admin with `manage_email_templates` permission

## Feature Testing

### 1. Image Library Access
- [ ] Can access: http://localhost:5000/admin/image-library
- [ ] Page loads without errors
- [ ] "Upload Image" button is visible
- [ ] Filter dropdown is working

### 2. Image Upload
- [ ] Click "Upload Image" button → Modal opens
- [ ] Select an image file (PNG, JPG, GIF, or SVG)
- [ ] Preview shows before upload
- [ ] Can add description
- [ ] Can select usage type
- [ ] Upload succeeds
- [ ] Success message appears
- [ ] Image appears in grid

### 3. Image Details
- [ ] Click on uploaded image or "View Details"
- [ ] Image displays correctly
- [ ] File information is accurate
- [ ] All copy buttons work:
  - [ ] Email Template (CID) code
  - [ ] Ticket/Token Template code
  - [ ] Direct URL
  - [ ] CID Only
- [ ] "Copy to clipboard" shows success toast

### 4. Image Filtering
- [ ] Filter by "All Images" - shows all
- [ ] Filter by "Email Templates" - shows email + all
- [ ] Filter by "Tickets" - shows ticket + all
- [ ] Filter by "Tokens" - shows token + all

### 5. Image Deletion
- [ ] Click "Delete" on an image
- [ ] Confirmation dialog appears
- [ ] After confirmation, image is removed from list
- [ ] Image is soft-deleted (check database: `is_active = false`)

### 6. Integration - Settings Page
- [ ] Go to: http://localhost:5000/admin/settings
- [ ] "Image Library" button exists in Quick Links
- [ ] Button redirects to image library page

### 7. Integration - CSS Guide
- [ ] Go to: http://localhost:5000/admin/css-guide
- [ ] "Images" link in quick nav
- [ ] "Image Library" button in top nav
- [ ] Images section exists with:
  - [ ] CID explanation
  - [ ] Direct URL explanation
  - [ ] Styling examples
  - [ ] Use case examples

### 8. API Documentation
- [ ] Go to: http://localhost:5000/api/docs
- [ ] "Image Attachments" tag exists
- [ ] All 6 endpoints documented:
  - [ ] POST /api/attachments/upload
  - [ ] GET /api/attachments/
  - [ ] GET /api/attachments/<id>
  - [ ] GET /api/attachments/image/<id>
  - [ ] PUT /api/attachments/<id>
  - [ ] DELETE /api/attachments/<id>

## Usage Testing

### 9. Use in Email Template
- [ ] Upload a logo image
- [ ] Copy the "Email Template (CID)" code
- [ ] Go to: http://localhost:5000/admin/email-templates
- [ ] Create or edit a template
- [ ] Paste the CID code in HTML
- [ ] Preview shows the image
- [ ] Send test email
- [ ] Email received with embedded image

### 10. Use in Ticket Designer
- [ ] Upload an image
- [ ] Copy the "Ticket/Token Template" code
- [ ] Go to: http://localhost:5000/admin/ticket-designer
- [ ] Select an event
- [ ] Paste the code in HTML section
- [ ] Preview shows the image
- [ ] Generate ticket PDF
- [ ] PDF contains the image

### 11. Use in Token Designer
- [ ] Upload an image
- [ ] Copy the "Ticket/Token Template" code
- [ ] Go to: http://localhost:5000/admin/token-designer
- [ ] Select an event
- [ ] Paste the code in HTML section
- [ ] Preview shows the image
- [ ] Generate token/badge PDF
- [ ] PDF contains the image

## Security & Permissions Testing

### 12. File Upload Validation
- [ ] Try uploading a text file → Should fail
- [ ] Try uploading a file > 5MB → Should fail
- [ ] Upload valid image < 5MB → Should succeed

### 13. Permission Checks
- [ ] Login as user WITHOUT `manage_email_templates`
- [ ] Try to access: /admin/image-library
- [ ] Should see permission error or redirect
- [ ] Login as user WITH permission
- [ ] Can access and use all features

### 14. API Direct Access
- [ ] Try GET /api/attachments/ without auth → 401 error
- [ ] Try POST /api/attachments/upload without auth → 401 error
- [ ] Try with valid auth → Success

## Database Verification

### 15. Database Checks
```sql
-- Check table exists
SELECT * FROM image_attachments LIMIT 5;

-- Check uploaded images
SELECT id, original_filename, content_type, file_size, usage_type, is_active 
FROM image_attachments 
WHERE is_active = true;

-- Check uploader tracking
SELECT ia.original_filename, au.name as uploader, ia.created_at
FROM image_attachments ia
JOIN admin_users au ON ia.uploaded_by = au.id;
```

## File System Verification

### 16. File Storage
```bash
# Check upload directory
ls -la uploads/attachments/

# Verify files exist
# Should see UUID-named files: abc-123-xyz.png, etc.

# Check file permissions
# Files should be readable
```

## Error Handling

### 17. Error Scenarios
- [ ] Upload with no file selected → Proper error message
- [ ] Upload invalid file type → Clear error message
- [ ] Upload file too large → Size limit error shown
- [ ] Delete already deleted image → Handles gracefully
- [ ] Access non-existent image → 404 error

## Performance

### 18. Performance Checks
- [ ] Upload completes within reasonable time (< 5 seconds)
- [ ] Image grid loads quickly (< 2 seconds for 20+ images)
- [ ] Image preview renders instantly
- [ ] File serving is fast (< 1 second)

## Browser Compatibility

### 19. Cross-Browser Testing (Optional)
- [ ] Chrome - All features work
- [ ] Firefox - All features work
- [ ] Edge - All features work
- [ ] Safari - All features work (if available)

## Documentation

### 20. Documentation Verification
- [ ] Read: `docs/IMAGE_ATTACHMENTS_IMPLEMENTATION.md`
- [ ] Read: `docs/IMAGE_SYSTEM_COMPLETE.md`
- [ ] CSS Guide has image examples
- [ ] API docs are complete and accurate

---

## Summary Checklist

Essential Tests (Must Pass):
- [ ] Upload works
- [ ] Images display in library
- [ ] Copy codes work
- [ ] Integration with templates works
- [ ] Email CID embedding works
- [ ] Ticket/Token PDF rendering works
- [ ] Permissions enforced
- [ ] File validation works

Nice-to-Have Tests:
- [ ] Filtering works
- [ ] Deletion works
- [ ] API documentation complete
- [ ] CSS guide helpful
- [ ] Performance acceptable
- [ ] Error messages clear

---

## Issue Reporting

If any test fails, report with:
1. Which test failed (number and description)
2. What you expected to happen
3. What actually happened
4. Any error messages (browser console, server logs)
5. Screenshots if applicable

---

## Status Tracking

**Date Started**: _______________  
**Tested By**: _______________  
**Tests Passed**: ___ / 20  
**Status**: [ ] All Pass [ ] Some Fail [ ] Not Started  

**Notes**:
_________________________________________________
_________________________________________________
_________________________________________________
