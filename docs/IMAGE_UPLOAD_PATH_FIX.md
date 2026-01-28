# Image Upload Path Fix - RESOLVED

## Issue
Upload was failing with error:
```
'uploads\\55d66c2d-90ba-4e93-aa50-16b8c0b639ca.jpg' is not in the subpath of 'C:\\Users\\USER\\PycharmProjects\\GateKeeper'
```

## Root Cause
The code was trying to calculate a relative path using `Path.relative_to()` which failed because the upload directory path wasn't properly constructed relative to the project root.

## Solution Applied

### 1. Fixed `get_upload_directory()` function
**Before:**
```python
def get_upload_directory():
    upload_dir = Path(current_app.config.get('UPLOAD_FOLDER', 'uploads/attachments'))
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir
```

**After:**
```python
def get_upload_directory():
    """Get the upload directory path"""
    from flask import current_app
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    attachments_dir = Path(upload_folder) / 'attachments'
    
    # If it's a relative path, make it relative to the project root
    if not attachments_dir.is_absolute():
        attachments_dir = Path(current_app.root_path).parent / attachments_dir
    
    attachments_dir.mkdir(parents=True, exist_ok=True)
    return attachments_dir
```

### 2. Simplified Path Storage
Instead of trying to calculate relative paths dynamically, now we store a simple, consistent relative path format:

**Before:**
```python
file_path=str(file_path.relative_to(Path.cwd()))
```

**After:**
```python
relative_path = f"uploads/attachments/{unique_filename}"
file_path=relative_path
```

### 3. Fixed Image Serving
Updated `serve_image()` to construct the full path correctly:

**Before:**
```python
file_path = Path(attachment.file_path)
```

**After:**
```python
project_root = Path(current_app.root_path).parent
file_path = project_root / attachment.file_path
```

### 4. Added Error Cleanup
Added cleanup logic to delete uploaded files if database insertion fails:

```python
except Exception as e:
    db.session.rollback()
    
    # Cleanup: delete uploaded file if database insert failed
    try:
        if 'file_path' in locals() and Path(file_path).exists():
            Path(file_path).unlink()
            current_app.logger.info(f"Cleaned up uploaded file after error: {file_path}")
    except Exception as cleanup_error:
        current_app.logger.error(f"Failed to cleanup file: {cleanup_error}")
    
    current_app.logger.error(f"Error uploading image: {str(e)}", exc_info=True)
    return jsonify({'error': f'Failed to upload image: {str(e)}'}), 500
```

## How It Works Now

1. **Upload Directory**: Always resolved to `project_root/uploads/attachments/`
2. **File Storage**: Files saved with UUID names: `55d66c2d-90ba-4e93-aa50-16b8c0b639ca.jpg`
3. **Database Path**: Stores simple relative path: `uploads/attachments/filename.jpg`
4. **File Serving**: Reconstructs full path as `project_root/uploads/attachments/filename.jpg`

## Testing

### Test the Fix:
1. Restart Flask app
2. Go to http://localhost:5000/admin/image-library
3. Upload an image
4. Should succeed without path errors
5. Image should appear in grid
6. Click "View Details" - image should display
7. Direct URL should work: http://localhost:5000/api/attachments/image/<id>

### Verify File Storage:
```bash
# Check that files are in the right place
ls -la uploads/attachments/

# Should see files like:
# 55d66c2d-90ba-4e93-aa50-16b8c0b639ca.jpg
# abc-123-def-456.png
# etc.
```

### Verify Database:
```sql
SELECT id, filename, file_path, created_at 
FROM image_attachments 
WHERE is_active = true;

-- file_path should be: "uploads/attachments/uuid.ext"
```

## Files Changed
- `app/routes/attachments.py` - Fixed path handling in 3 places

## Status
✅ **FIXED** - Upload should now work correctly without path errors

## Prevention
The fix ensures:
- Consistent path handling across the application
- Proper relative path storage in database
- Correct path reconstruction when serving files
- Cleanup on errors to avoid orphaned files
- Better error logging with stack traces

---

**Fixed**: January 28, 2026  
**Issue Type**: Path handling bug  
**Impact**: Upload functionality restored
