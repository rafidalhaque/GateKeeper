# Celery Worker Fix - Ticket Generation Issue

## Problem
When generating tickets in bulk, you're getting this error:
```
ValueError: not enough values to unpack (expected 3, got 0)
File "celery/app/trace.py", line 664, in fast_trace_task
    tasks, accept, hostname = _loc
```

## Root Cause
This is a Celery task registration issue. The tasks are not being properly discovered by the Celery worker, causing it to fail when trying to execute them.

## What Was Fixed

### 1. ✅ Updated `app/celery_app.py`
- Added explicit task module inclusion: `include=['app.services.tasks']`
- Fixed Flask app context handling with cached app instance
- Added worker configuration parameters

### 2. ✅ Created `celery_worker.py`
- Proper entry point for Celery worker
- Ensures Flask app and tasks are initialized before worker starts

## How to Fix Your Running System

### Step 1: Stop Current Celery Worker
If you have a Celery worker running, stop it:
```bash
# Press Ctrl+C in the terminal where Celery is running
```

### Step 2: Restart Redis (if needed)
Make sure Redis is running:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it:
redis-server
```

### Step 3: Start Celery Worker with New Configuration

**On Windows (recommended):**
```bash
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**On Linux/Mac:**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

### Step 4: Verify Tasks Are Registered

After starting the worker, you should see output like:
```
[tasks]
  . app.services.tasks.generate_tickets_task
  . app.services.tasks.import_csv_task
  . app.services.tasks.send_bulk_emails_task
```

If you see this, the tasks are properly registered! ✅

## Testing

### Test 1: Check Celery Worker Status
After starting the worker, it should show:
```
-------------- celery@YOUR-COMPUTER v5.x.x
--- ***** -----
-- ******* ---- Windows-10-... 
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         gatekeeper
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ----
--- ***** -----
-------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . app.services.tasks.generate_tickets_task
  . app.services.tasks.import_csv_task
  . app.services.tasks.send_bulk_emails_task

[... ready to receive tasks]
```

### Test 2: Generate Tickets
1. Go to your Flask admin panel
2. Select an event
3. Click "Generate Tickets" or "Send Bulk Tickets"
4. Check the Celery worker terminal - you should see:
   ```
   [INFO/MainProcess] Task app.services.tasks.generate_tickets_task[...] received
   [INFO/MainProcess] Task app.services.tasks.generate_tickets_task[...] succeeded
   ```

### Test 3: Check Redis
You can verify tasks in Redis:
```bash
redis-cli
> KEYS *
# Should show celery keys

> exit
```

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'app'"
**Solution:** Make sure you're running Celery from the project root directory where `app/` folder exists.

```bash
cd C:\Users\USER\PycharmProjects\GateKeeper
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

### Issue 2: Still getting "not enough values to unpack"
**Solution:** 
1. Make sure you restarted the Celery worker after the changes
2. Clear Redis cache:
   ```bash
   redis-cli FLUSHALL
   ```
3. Restart both Flask and Celery

### Issue 3: "Connection refused to Redis"
**Solution:** Start Redis first:
```bash
# Windows (if installed via Chocolatey or MSI)
redis-server

# Or if using WSL/Docker
docker run -d -p 6379:6379 redis:alpine
```

### Issue 4: Tasks complete but no PDFs generated
**Solution:** Check that WeasyPrint dependencies are installed:
```bash
pip install weasyprint
# Windows may need: pip install pycairo pyGObject
```

## Development Workflow

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: Flask App
```bash
cd C:\Users\USER\PycharmProjects\GateKeeper
.venv\Scripts\activate
flask --app run.py run
```

### Terminal 3: Celery Worker
```bash
cd C:\Users\USER\PycharmProjects\GateKeeper
.venv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

## Why `--pool=solo` on Windows?

Windows doesn't support `fork()` which is required by the default `prefork` pool. Using `--pool=solo` runs tasks in the main process, which works on Windows.

Alternative pools for Windows:
- `--pool=solo` - Single process (recommended for development)
- `--pool=gevent` - Requires: `pip install gevent`
- `--pool=eventlet` - Requires: `pip install eventlet`

## Production Recommendations

For production deployment:
1. Use a process manager like **Supervisor** (Linux) or **NSSM** (Windows)
2. Set up proper logging
3. Use `--pool=gevent` or `--pool=eventlet` for better concurrency
4. Monitor with Flower: `pip install flower && celery -A celery_worker.celery flower`

## Quick Start Script

Create `start_workers.bat` (Windows) or `start_workers.sh` (Linux):

**Windows (start_workers.bat):**
```batch
@echo off
echo Starting Celery Worker for GateKeeper...
cd /d "%~dp0"
call .venv\Scripts\activate
celery -A celery_worker.celery worker --loglevel=info --pool=solo
pause
```

**Linux (start_workers.sh):**
```bash
#!/bin/bash
echo "Starting Celery Worker for GateKeeper..."
cd "$(dirname "$0")"
source .venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

## Verification Checklist

After restarting Celery worker:
- [ ] Redis is running
- [ ] Celery worker shows 3 registered tasks
- [ ] Celery worker shows "ready to receive tasks"
- [ ] No errors in Celery worker startup
- [ ] Flask app is running
- [ ] Try generating tickets - check Celery terminal for task execution

## Expected Output on Success

### Celery Worker Terminal:
```
[INFO/MainProcess] Task app.services.tasks.generate_tickets_task[abc-123] received
[INFO/MainProcess] Generating tickets for event: xyz-456
[INFO/MainProcess] Generated 50 tickets successfully
[INFO/MainProcess] Task app.services.tasks.generate_tickets_task[abc-123] succeeded in 3.456s
```

### Flask App Terminal:
```
127.0.0.1 - - [28/Jan/2026 00:00:00] "POST /api/tickets/generate HTTP/1.1" 202 -
```

202 status means the task was accepted and queued successfully!

## Need More Help?

If you're still having issues:
1. Check Celery worker logs for specific errors
2. Check Flask app logs
3. Verify Redis is accessible: `redis-cli ping`
4. Make sure all dependencies are installed: `pip install -r requirements.txt`

## Files Modified

- ✅ `app/celery_app.py` - Fixed task registration and Flask context
- ✅ `celery_worker.py` - Created proper entry point
- ✅ This guide - Complete troubleshooting documentation
