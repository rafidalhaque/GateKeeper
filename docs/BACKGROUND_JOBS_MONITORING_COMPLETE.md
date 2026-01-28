# ✅ Background Jobs Monitoring - COMPLETE

## Overview
I've implemented a comprehensive background jobs monitoring system that displays all Celery tasks and their progress in real-time in the frontend.

---

## Features Implemented

### 📊 Dashboard Stats
- **Total Jobs** - All background jobs ever run
- **Queued** - Jobs waiting to be processed
- **Processing** - Jobs currently running
- **Completed** - Successfully finished jobs
- **Failed** - Jobs that encountered errors

### 📋 Jobs List
- **Real-time status** for each job
- **Progress bars** showing completion percentage
- **Task details** including:
  - Task name (user-friendly names)
  - Status badge (color-coded)
  - Progress percentage
  - Items processed / total items
  - Created timestamp
  - Duration (calculated dynamically)

### 🔧 Controls
- **Filter by status** - View all, queued, processing, completed, or failed jobs
- **Auto-refresh toggle** - Automatically refresh every 5 seconds
- **Manual refresh button** - Update on demand
- **Clear completed** - Remove all completed jobs from list
- **Delete individual jobs** - Remove specific job records

### 📱 Additional Features
- **Error details modal** - View full error messages for failed jobs
- **Color-coded status badges**:
  - 🔵 Queued (info)
  - 🟡 Processing (warning)
  - 🟢 Completed (success)
  - 🔴 Failed (error)
- **Progress bars** with color matching status
- **Responsive design** - Works on mobile and desktop

---

## API Endpoints Created

### `GET /api/jobs/`
List all background jobs with optional status filter.

**Parameters:**
- `status` (optional) - Filter by status: queued, processing, completed, failed
- `limit` (optional, default: 50) - Maximum number of jobs to return

**Response:**
```json
[
  {
    "id": "uuid",
    "task_name": "app.services.tasks.generate_tickets_task",
    "task_id": "celery-task-id",
    "status": "completed",
    "progress": 100,
    "total_items": 50,
    "processed_items": 50,
    "error_message": null,
    "created_at": "2026-01-28T10:00:00",
    "started_at": "2026-01-28T10:00:01",
    "completed_at": "2026-01-28T10:00:15"
  }
]
```

### `GET /api/jobs/<task_id>`
Get status of a specific job.

### `GET /api/jobs/active`
Get all active (queued or processing) jobs.

### `GET /api/jobs/stats`
Get job statistics.

**Response:**
```json
{
  "total": 150,
  "queued": 2,
  "processing": 1,
  "completed": 140,
  "failed": 7,
  "active": 3
}
```

### `DELETE /api/jobs/<task_id>`
Delete a job record (only completed or failed jobs).

### `POST /api/jobs/clear-completed`
Clear all completed jobs.

---

## Frontend Page

### Location
**URL:** `/admin/jobs`
**Template:** `app/templates/admin/jobs.html`
**Navigation:** Admin sidebar → "Background Jobs"

### Features

#### 1. Statistics Cards
Five cards showing real-time counts:
- Total jobs with server icon
- Queued jobs with clock icon
- Processing jobs with spinner
- Completed jobs with checkmark icon
- Failed jobs with error icon

#### 2. Filter Buttons
Quick access buttons to filter jobs by status:
- All Jobs (primary)
- Queued (info)
- Processing (warning)
- Completed (success)
- Failed (error)

#### 3. Jobs Table
Displays all jobs with columns:
- **Task** - Friendly name + task ID preview
- **Status** - Color-coded badge
- **Progress** - Visual progress bar + percentage
- **Items** - Processed / Total
- **Created** - Timestamp
- **Duration** - Calculated time
- **Actions** - View error / Delete buttons

#### 4. Auto-refresh
Toggle switch to enable/disable automatic refresh every 5 seconds.

---

## How It Works

### 1. Task Creation
When a Celery task starts, it creates a `CeleryJob` record:

```python
job = CeleryJob(
    task_name='generate_tickets',
    task_id=self.request.id,
    status='processing',
    started_at=datetime.utcnow()
)
db.session.add(job)
db.session.commit()
```

### 2. Progress Updates
Tasks update the job record during execution:

```python
job.progress = 50  # 0-100
job.processed_items = 25
job.total_items = 50
db.session.commit()
```

### 3. Completion
When finished, task updates final status:

```python
job.status = 'completed'  # or 'failed'
job.progress = 100
job.completed_at = datetime.utcnow()
db.session.commit()
```

### 4. Frontend Display
Frontend polls the API and displays jobs in real-time with:
- Color-coded status
- Progress visualization
- Duration calculation
- Error details (if failed)

---

## Supported Tasks

Currently tracking these Celery tasks:
1. **CSV Import** (`import_csv_task`)
   - Imports participants from CSV files
   - Shows progress as rows are processed

2. **Generate Tickets** (`generate_tickets_task`)
   - Generates PDF tickets for participants
   - Shows total tickets generated

3. **Send Bulk Emails** (`send_bulk_emails_task`)
   - Sends emails to multiple recipients
   - Shows emails sent / total

---

## Usage Examples

### Monitor Jobs in Real-time
1. Go to `/admin/jobs`
2. Enable auto-refresh toggle
3. Watch jobs update every 5 seconds

### View Failed Jobs
1. Click "Failed" filter button
2. Click eye icon on any failed job
3. View full error message in modal

### Clear Old Jobs
1. Click "Clear Completed" button
2. Confirm deletion
3. All completed jobs are removed

### Check Specific Task
1. Find task in the table
2. View progress bar and percentage
3. Check duration and items processed

---

## Database Schema

The `celery_jobs` table stores:

```python
id: UUID (primary key)
task_name: String (e.g., 'generate_tickets')
task_id: String (Celery task ID)
status: String (queued, processing, completed, failed)
progress: Integer (0-100)
total_items: Integer (optional)
processed_items: Integer (default 0)
error_message: Text (for failed jobs)
created_at: DateTime
started_at: DateTime
completed_at: DateTime
```

---

## Files Created/Modified

### Created:
✅ `app/routes/jobs.py` - API endpoints for job monitoring
✅ `app/templates/admin/jobs.html` - Frontend monitoring page

### Modified:
✅ `app/app.py` - Registered jobs blueprint
✅ `app/routes/frontend.py` - Added `/admin/jobs` route
✅ `app/templates/admin/components/nav.html` - Added navigation link

### Existing (Using):
✅ `app/models/events.py` - `CeleryJob` model (already exists)
✅ `app/services/tasks.py` - Tasks already create job records

---

## Screenshots (What You'll See)

### Stats Cards
```
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Total Jobs  │   Queued    │ Processing  │  Completed  │   Failed    │
│     150     │      2      │      1      │     140     │      7      │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### Jobs Table
```
┌──────────────────┬──────────┬──────────────┬─────────┬──────────┬──────────┬─────────┐
│ Task             │ Status   │ Progress     │ Items   │ Created  │ Duration │ Actions │
├──────────────────┼──────────┼──────────────┼─────────┼──────────┼──────────┼─────────┤
│ Generate Tickets │ [✓] Done │ [████] 100%  │ 50/50   │ 10:00 AM │ 15s      │ [🗑]    │
│ CSV Import       │ [⏳] Run  │ [██░░] 50%   │ 25/50   │ 10:05 AM │ 8s       │         │
│ Send Emails      │ [⏰] Wait │ [░░░░] 0%    │ 0/100   │ 10:10 AM │ -        │         │
│ Generate Tickets │ [✗] Fail │ [████] 100%  │ -       │ 09:50 AM │ 2s       │ [👁][🗑] │
└──────────────────┴──────────┴──────────────┴─────────┴──────────┴──────────┴─────────┘
```

---

## Configuration

### Auto-refresh Interval
Default: 5 seconds

To change, edit in `app/templates/admin/jobs.html`:
```javascript
}, 5000); // Change this value (milliseconds)
```

### Jobs List Limit
Default: 50 jobs

To change, edit in `app/routes/jobs.py`:
```python
limit = request.args.get('limit', 50, type=int)  # Change 50
```

---

## Testing

### Test Job Creation
1. Go to an event
2. Click "Generate Tickets"
3. Go to `/admin/jobs`
4. Should see new job with "processing" status

### Test Progress Updates
1. Enable auto-refresh
2. Watch job progress bar update
3. Should reach 100% when complete

### Test Failed Jobs
1. Create a job that will fail (e.g., invalid data)
2. Go to `/admin/jobs`
3. Click "Failed" filter
4. Click eye icon to view error

### Test Clear Completed
1. Have some completed jobs
2. Click "Clear Completed" button
3. Completed jobs should disappear

---

## Permissions

All endpoints require admin authentication:
- `@admin_required` - Must be logged in as admin
- No specific permission required (all admins can view)

---

## Future Enhancements (Optional)

Could be added later:
- 📊 Chart showing job trends over time
- 🔔 Notifications when jobs complete/fail
- ⏸️ Ability to pause/cancel running jobs
- 📥 Export job history to CSV
- 🔄 Retry failed jobs
- 📈 Performance metrics (avg duration, success rate)
- 🎨 Customizable refresh interval
- 🔍 Search/filter by task name or date range

---

## Summary

✅ **Complete job monitoring system** with real-time updates
✅ **API endpoints** for job management  
✅ **Frontend dashboard** with statistics and controls  
✅ **Auto-refresh** for live monitoring  
✅ **Error handling** with detailed error views  
✅ **Job management** (view, filter, delete, clear)  

**Navigate to `/admin/jobs` to see all background tasks!** 🚀

The system is fully functional and ready to use. All Celery tasks (CSV import, ticket generation, bulk emails) will automatically appear in the monitoring dashboard with real-time progress updates.
