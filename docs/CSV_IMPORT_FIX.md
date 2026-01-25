# CSV Import Celery Error Fix

## Problem

When uploading a CSV file for import, Celery was throwing the following error:

```
ValueError: not enough values to unpack (expected 3, got 0)
```

This occurred at line `tasks, accept, hostname = _loc` in Celery's `fast_trace_task` function.

## Root Cause

The error was caused by improper Flask-Celery integration. The issue was:

1. **Thread-local storage not initialized**: Celery's `fast_trace_task` uses thread-local storage (`_loc`) to cache task information, but this wasn't being properly initialized in the worker processes.

2. **Worker process initialization issues**: Using `worker_process_init` signal to push a single Flask app context was problematic because:
   - The app context was pushed once at worker startup but never properly managed
   - Context-local variables weren't properly isolated between tasks
   - Thread-local storage used by Celery wasn't synchronized with Flask's app context

## Solution

The fix involved restructuring how Flask app context is managed in Celery tasks:

### 1. Updated `app/celery_app.py`

**Before:**
```python
@worker_process_init.connect
def init_worker_process(sender=None, **kwargs):
    global flask_app
    from app.app import create_app
    
    flask_app = create_app()
    flask_app.app_context().push()

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)
```

**After:**
```python
class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context"""
    def __call__(self, *args, **kwargs):
        from app.app import create_app
        
        # Create Flask app and push context for each task call
        app = create_app()
        with app.app_context():
            return self.run(*args, **kwargs)
```

**Key improvements:**
- Removed `worker_process_init` signal handler
- Each task now creates its own Flask app instance and context
- Context is properly managed with `with` statement (automatic cleanup)
- Added `task_track_started=True` to Celery config for better task tracking

### 2. Updated `app/services/csv_import.py`

Removed redundant app context creation in `process_csv_import()` function since it's now called from within a Celery task that already has proper app context.

**Before:**
```python
def process_csv_import(event_id, csv_content):
    from app.app import create_app
    app = create_app()
    
    with app.app_context():
        # ... process CSV
```

**After:**
```python
def process_csv_import(event_id, csv_content):
    # ... process CSV directly (already in app context)
```

## How to Test

1. **Restart Celery worker:**
   ```bash
   celery -A app.celery_app.celery worker --loglevel=info --pool=solo
   ```

2. **Upload CSV file:**
   - Navigate to the event management page
   - Upload the `examples/solo_mode_import.csv` file
   - The import should complete successfully

3. **Check logs:**
   - You should see task received and completed messages
   - No `ValueError` should occur

## CSV Format Reference

### Solo Mode
```csv
participant_name,participant_email,t-shirt_size
John Doe,john@example.com,M
Jane Smith,jane@example.com,S
```

### Team Mode
```csv
team_id,team_name,member_name,member_email,t-shirt_size
1,Team Alpha,John Doe,john@example.com,M
1,Team Alpha,Jane Smith,jane@example.com,S
2,Team Beta,Bob Johnson,bob@example.com,L
```

## Additional Notes

- The solution creates a new Flask app instance for each task, which has minimal performance impact in typical usage
- This approach ensures complete isolation between tasks and prevents context leakage
- The `with app.app_context()` ensures proper cleanup even if the task fails

## Related Files

- `app/celery_app.py` - Celery configuration and Flask integration
- `app/services/tasks.py` - Celery task definitions
- `app/services/csv_import.py` - CSV processing logic
- `app/routes/csv_import.py` - API endpoints for CSV import
