# Onsite Event Dashboard – System Plan (Updated)

## 1. Goal
Build a **self-hosted onsite event management system** that supports:
- Solo and team-based events
- Secure QR-based attendance check-in
- Ticketing with PDF + email delivery
- Admin-controlled attendee management
- Privacy-safe attendee views
- Onsite booth-friendly QR scanning
- Background job processing for email and PDF generation

Designed for **real-world events**, unstable internet, and fast check-in.

---

## 2. Tech Stack

### Backend
- Python 3.10+
- Flask
- SQLAlchemy (ORM)
- Jinja2 (templates for email + tickets)
- Celery (background job queue)
- Redis (Celery broker + result backend)

### Frontend
- TailwindCSS
- DaisyUI
- Alpine.js (lightweight interactivity)
- Browser Camera API (QR scanning)

### Database
- **PostgreSQL** (recommended for production)
  - Better UUID support
  - Native JSONB fields
  - Superior concurrency handling
  - ACID compliance
  - Better for complex queries and scalability
- MySQL support available for compatibility, but PostgreSQL is the primary target

### Authentication
- Supabase Auth
- JWT-based auth validation in Flask
- Session-based auth state for admin/manager roles

### PDF Generation
- WeasyPrint (Python-native, easier Docker integration)

### Other
- SMTP (custom, admin-configurable)
- QR generation: `qrcode` / `segno`
- Background Jobs: Celery + Redis

---

## 3. Roles & Access Model

### Super Admin
- Full, unrestricted access
- Can manage:
  - Events
  - Roles
  - Permissions
  - Admins / Booth Managers
  - System-level configuration
- Created via CLI command or .env configuration (see Section 7)

### Admin
- Full control over assigned events
- CSV import
- Ticket template design
- Email sending
- Attendance reporting
- Manual add/edit/delete participants & teams
- **No passcode required when authenticated**

### Booth Manager
- Access QR scanner page
- Can mark attendance **without passcode when authenticated**
- Limited to check-in related features
- Read-only access to participant data

### Attendee (Public)
- Access only their **own ticket page**
- Can see only self data (and team name/id if applicable)

---

## 4. Event Configuration

Each event has:
- `mode`: `solo` | `team`
- Optional attendance `passcode` (for fallback/public scanner links only)
- Ticket HTML + CSS template
- SMTP configuration reference
- Custom fields (JSONB) for event-specific data collection
- Schedule configuration (optional, for prayer times or breaks)

Event mode determines:
- CSV format
- UI behavior
- Attendance logic

**Note:** Passcode is only required for unauthenticated access. Authenticated admins/managers bypass passcode checks entirely.

---

## 5. Database Schema (Core)

### events
- id (uuid, pk)
- name
- date
- venue
- mode (`solo` | `team`)
- passcode (nullable, for fallback/public access)
- ticket_template_html
- ticket_template_css
- custom_fields (jsonb) - flexible field configuration (e.g., dietary preferences, emergency contact)
- schedule_config (jsonb) - prayer times, breaks, session timings
- created_at
- updated_at

### teams
- id (integer, pk, auto-increment)
- uuid (uuid, unique)
- event_id (fk → events.id)
- team_name
- is_empty (boolean, default=false) - auto-updated when last member is removed
- created_at
- updated_at

### participants
- id (uuid, pk)
- event_id (fk → events.id)
- team_id (fk → teams.id, nullable)
- name
- email
- t_shirt_size (nullable, configurable per event)
- custom_data (jsonb) - stores event-specific custom field values
- unique_url_uuid (uuid, unique)
- attendance_status (boolean, default=false)
- attended_at (timestamp, nullable)
- created_at
- updated_at

### email_logs
- id (integer, pk)
- event_id (fk → events.id)
- recipient_email
- subject
- template_name
- status (`queued` | `sent` | `failed`)
- error_message (nullable)
- retry_count (integer, default=0)
- next_retry_at (timestamp, nullable)
- created_at
- sent_at (timestamp, nullable)

### checkin_logs
- id (integer, pk)
- participant_id (fk → participants.id)
- event_id (fk → events.id)
- checked_in_by (fk → admin_users.id, nullable) - null if self-check-in
- ip_address (string, nullable)
- user_agent (text, nullable)
- device_fingerprint (string, nullable)
- checked_in_at (timestamp)

### celery_jobs
- id (uuid, pk)
- task_name (string) - e.g., 'send_bulk_emails', 'generate_tickets'
- task_id (string, unique) - Celery task ID
- status (`queued` | `processing` | `completed` | `failed`)
- progress (integer, 0-100)
- total_items (integer)
- processed_items (integer)
- error_message (text, nullable)
- created_at
- started_at (timestamp, nullable)
- completed_at (timestamp, nullable)

---

## 6. RBAC Database Schema

### roles
- id (integer, pk)
- name (string, unique)
- description
- created_at
- updated_at

### permissions
- id (integer, pk)
- key (string, unique) - example: `participant.read`
- description
- feature_group (string)
- system_reserved (boolean = true)

### role_permissions
- role_id (fk → roles.id)
- permission_id (fk → permissions.id)
- composite primary key (role_id, permission_id)

### admin_users
- id (uuid, pk)
- supabase_user_id (string, unique)
- role_id (fk → roles.id)
- created_at
- updated_at

---

## 7. Super Admin Bootstrap & Initial Setup

### Option A: CLI Command (Recommended - More Secure)
```bash
flask create-super-admin --email admin@example.com --name "Admin Name"
```

**Why CLI is better:**
- No credentials in .env file (more secure)
- Can be run during deployment
- Generates secure random password
- Immediate email notification
- Auditable via deployment logs

### Option B: Environment Variable (Fallback)
```env
SUPER_ADMIN_EMAIL=admin@example.com
SUPER_ADMIN_NAME=Admin Name
SUPER_ADMIN_PASSWORD=secure_password_here
```

**Only use during initial setup, then remove from .env**

### Implementation
- CLI command creates Supabase user + admin_users record
- Assigns default "Super Admin" role
- Sends setup email with login credentials
- Logs creation in audit trail

**Recommendation:** Use CLI for production, .env for development/testing only.

---

## 8. CSV Import Logic

### Team Mode CSV

```csv
team_id,team_name,member_name,member_email,t-shirt_size
```

Behavior:
- Group rows by `team_id`
- Create one `teams` row per team_id
- Create multiple `participants` linked to `teams.id`
- Generate UUID for each participant
- **Background job (Celery)** for processing

### Solo Mode CSV

```csv
participant_name,participant_email,t-shirt_size
```

Behavior:
- One participant per row
- `team_id = NULL`
- UUID generated per participant
- **Background job (Celery)** for processing

### Import Process
1. Admin uploads CSV
2. System validates format
3. Celery job queued
4. Progress bar updates in real-time
5. Email notifications on completion
6. Error log for failed rows

---

## 9. Admin CRUD Features

Admin can:
- Edit participant details
- Delete participant (auto-updates team `is_empty` flag)
- Add participant manually
- Add/edit/delete teams
- Reassign participants to teams (team mode only)
- View and manage empty teams (filter by `is_empty=true`)
- Bulk delete empty teams

### Team Management Logic
- When last member is removed from a team → `is_empty = true`
- When new member is added to empty team → `is_empty = false`
- Admin can manually delete empty teams or set up auto-cleanup policies

CSV import is **not final**—admin always has control.

---

## 10. Ticket System

### Ticket Contents
- Event details
- Instructions
- Participant details
- Team name & team_id (if team mode)
- Custom field values (if configured)
- QR code (unique URL)

### Ticket Design
- Admin designs ticket using **HTML + CSS**
- Live preview in admin panel (Ticket Design Playground)
- Supports placeholders:
  - `{{participant_name}}`
  - `{{email}}`
  - `{{participant_uuid}}`
  - `{{team_name}}`
  - `{{team_id}}`
  - `{{qr_code}}`
  - `{{event_details}}`
  - `{{custom_fields.field_name}}` - access custom field values
  - `{{schedule}}` - prayer times or event schedule

### Delivery
- Tickets rendered as PDF via **WeasyPrint**
- **Background job queue (Celery)** for bulk generation
- Progress tracking in admin UI
- Bulk emailed via SMTP (also queued)
- Logged in email_logs table
- Retry logic for failed emails

### Performance
- Tickets generated asynchronously on CSV import
- Admin sees progress bar during generation
- Can regenerate individual tickets if needed

---

## 11. QR Code & Unique URL Logic

- Each participant has a **unique UUID-based URL**
- QR code encodes this URL only
- URL behavior depends on viewer authentication state

### If Unauthenticated (Public Attendee)
- Show ticket view
- Show only:
  - Name
  - Email
  - T-shirt size (if applicable)
  - Custom field values (if configured)
  - Team name/id (if applicable)
- **Passcode required** to mark attendance
- No access to others' data

### If Authenticated (Admin/Booth Manager)
- Show check-in panel
- **No passcode required** (auth bypasses passcode)
- Allow marking attendance immediately
- Log check-in with admin ID, IP, user agent
- Display participant info with team context

### Security
- All check-ins logged in `checkin_logs`
- IP and device fingerprint tracked for audit
- Prevents double check-in
- Rate limiting on check-in endpoint

---

## 12. Attendance Check-in (Three Ways)

### A. QR via Ticket URL
- Attendee/Admin scans QR with any scanner
- Opens URL in browser
- If authenticated (admin/manager): **immediate check-in, no passcode**
- If unauthenticated (public): **passcode required**

### B. Admin Panel QR Scanner Page

#### Scanner Page Features
- Live camera preview
- Browser-based QR scanning (Alpine.js + Camera API)
- **Quick Scan Mode** - scan multiple attendees without re-authentication
- Audio/vibration feedback on successful scan
- Mobile and tablet optimized

#### After Scan
- Fetch participant data by UUID
- Show:
  - Name
  - Email
  - T-shirt size
  - Custom field values
  - Event name
  - Team info (if team mode)
  - Previous check-in status

#### Action (Authenticated Session)
- **No passcode required** if admin/manager is logged in
- Click "Mark as Attended"
- Instant feedback (green checkmark + sound)
- Prevent double check-in
- Log to `checkin_logs`

#### Quick Scan Mode
- Enable/disable toggle in scanner UI
- When enabled: auto-mark attendance after scan
- When disabled: manual confirmation required
- Session persists across scans (no re-login needed)

### C. Offline Scan Queue (Phase 1.5 - MVP+)
- Cache scanned UUIDs in browser localStorage
- Queue check-ins when offline
- Auto-sync when connection restored
- Progress indicator for queued scans

---

## 13. Email System

### Features
- Admin-configurable SMTP
- HTML email templates with Jinja2
- **Background queue processing (Celery)**
- Bulk email sending with progress tracking
- Per-recipient logging
- Automatic retry logic (max 3 retries)
- Failed email dashboard

### Use Cases
- Ticket delivery
- Event instructions
- Announcements
- Follow-ups
- Reminder emails (prayer times, session start)

### Queue Management
- Emails added to Celery queue on bulk send
- Real-time progress updates in admin UI
- "Resend Failed Emails" button
- Filter emails by status (queued/sent/failed)
- Detailed error logs per recipient

### Performance
- Batch processing (configurable batch size)
- Rate limiting to respect SMTP limits
- Concurrent worker support

---

## 14. Security & Privacy

- UUID-based access (unguessable URLs)
- No public list endpoints
- Attendee sees **only self data**
- Admin-only APIs protected by Supabase JWT
- Passcode required **only for unauthenticated access**
- **Authenticated admins/managers bypass passcode**
- HTTPS strongly recommended (enforced in production)
- Rate limiting on all public endpoints
- CORS configuration for API security
- SQL injection protection via SQLAlchemy ORM
- XSS protection via template escaping
- CSRF tokens on all forms
- Session management with secure cookies
- Audit logging for all check-ins (`checkin_logs`)
- IP and device fingerprint tracking
- Secrets stored in environment variables only

---

## 15. API Endpoints (High-Level)

### Events
- POST `/api/events` - Create event
- GET `/api/events` - List events (admin only)
- GET `/api/events/<id>` - Event details
- PUT `/api/events/<id>` - Update event
- DELETE `/api/events/<id>` - Delete event

### Participants
- POST `/api/import/csv` - CSV import (queued job)
- POST `/api/participants` - Add participant
- PUT `/api/participants/<id>` - Update participant
- DELETE `/api/participants/<id>` - Delete participant
- GET `/api/participants?event_id=<id>` - List participants (admin)

### Teams
- POST `/api/teams` - Create team
- PUT `/api/teams/<id>` - Update team
- DELETE `/api/teams/<id>` - Delete team
- GET `/api/teams?is_empty=true` - List empty teams
- DELETE `/api/teams/bulk-delete-empty` - Clean up empty teams

### Check-in
- GET `/ticket/<uuid>` - Ticket page (public/auth-aware)
- POST `/api/checkin/lookup/<uuid>` - Get participant for scan
- POST `/api/checkin/confirm` - Mark attendance (auth-aware, no passcode if logged in)
- GET `/api/checkin/logs?event_id=<id>` - Check-in audit logs

### Email
- POST `/api/email/send-bulk` - Queue bulk emails (returns job ID)
- GET `/api/email/status/<job_id>` - Check email job progress
- POST `/api/email/retry-failed` - Retry failed emails
- GET `/api/email/logs?event_id=<id>` - Email logs

### Tickets
- POST `/api/tickets/generate` - Queue ticket generation (returns job ID)
- GET `/api/tickets/status/<job_id>` - Check generation progress
- GET `/api/tickets/download/<uuid>` - Download single ticket PDF

### Jobs (Celery)
- GET `/api/jobs/<job_id>` - Get job status and progress
- GET `/api/jobs?event_id=<id>` - List jobs for event

### Roles & Permissions (Super Admin)
- GET `/api/permissions` - List all permissions (grouped)
- POST `/api/roles` - Create role
- PUT `/api/roles/<id>` - Update role permissions
- DELETE `/api/roles/<id>` - Delete role
- GET `/api/admin-users` - List admins
- POST `/api/admin-users/<id>/assign-role` - Assign role

### Reports
- GET `/api/reports/attendance-summary?event_id=<id>` - Attendance stats
- GET `/api/reports/export-csv?event_id=<id>` - Export attendees CSV
- GET `/api/reports/team-stats?event_id=<id>` - Team-wise attendance
- GET `/api/reports/checkin-timeline?event_id=<id>` - Time-series data

---

## 16. Reporting & Analytics

### Real-Time Dashboard
- Total registered participants
- Total attended
- Attendance rate (%)
- Team-wise breakdown (if team mode)
- Check-in timeline graph (attendees per hour)
- Live updates during event

### Reports Available
1. **Attendance Summary**
   - Overall stats
   - Attended vs. registered
   - No-show count
   - Team performance (team mode)

2. **CSV Exports**
   - All participants with attendance status
   - Custom field data included
   - Team assignments
   - Check-in timestamps

3. **Check-in Timeline**
   - Time-series graph of check-ins
   - Peak hours identification
   - Helps plan future events

4. **Team Statistics** (Team Mode)
   - Team-wise attendance rate
   - Team size vs. attendance correlation
   - Empty teams list

5. **Email Delivery Report**
   - Sent/failed breakdown
   - Bounce tracking
   - Open rates (if SMTP supports tracking)

### Export Formats
- CSV (participants, teams, check-ins)
- PDF (formatted reports)
- JSON (API access for integrations)

---

## 17. MVP vs Later

### MVP (Phase 1)
- ✅ CSV import with background jobs
- ✅ Ticket PDF generation (queued)
- ✅ Email delivery (queued)
- ✅ QR attendance (auth-aware, no passcode for admins)
- ✅ Admin scanner page with Quick Scan Mode
- ✅ Basic reporting (attendance summary, CSV export)
- ✅ RBAC (roles + permissions)
- ✅ Super Admin CLI setup
- ✅ Custom fields (JSONB)
- ✅ Empty team management
- ✅ Check-in audit logs
- ✅ Email retry logic

### Phase 1.5 (MVP+)
- Offline scan cache + sync
- Progressive Web App (PWA) for scanner
- Ticket design playground (live preview)
- Advanced analytics dashboard
- Multi-event admin view

### Phase 2
- Booth manager session tokens (time-based auth)
- Badge printing integration
- Multi-language support
- Webhook notifications (Slack, Discord)
- API rate limiting per user
- Two-factor authentication
- Advanced audit trail with search

### Phase 3
- Mobile app (React Native)
- Kiosk mode for self-check-in
- NFC tag support
- Integration with payment gateways (paid events)
- Automated certificate generation

---

## 18. Definition of Done
- ✅ Admin can onboard 500+ attendees in <5 minutes (CSV import)
- ✅ Check-in takes <3 seconds per attendee (Quick Scan Mode)
- ✅ No data leakage (UUID-based access, role enforcement)
- ✅ Works on laptop, tablet, and mobile (responsive UI)
- ✅ No external SaaS dependency (except Supabase Auth)
- ✅ Background jobs for long-running tasks (email, PDF generation)
- ✅ Authenticated admins bypass passcode requirements
- ✅ Comprehensive audit trail (check-in logs, email logs)
- ✅ Custom field support for event-specific needs
- ✅ Empty team management with auto-flagging
- ✅ Failed email retry mechanism
- ✅ Real-time progress tracking for bulk operations
- ✅ Exportable reports (CSV, PDF)

---

## 19. Super Admin, Roles & Permission System

### 19.1 Roles Overview

The system supports **role-based access control (RBAC)** with:

- **Super Admin**
  - Full, unrestricted access
  - Can manage:
    - Events
    - Roles
    - Permissions
    - Admins / Booth Managers
    - System-level configuration
- **Custom Roles**
  - Created by Super Admin
  - Assigned to admin users
  - Permissions are granular and explicit

---

### 19.2 Permission Model

Permissions are **task-based**, auto-generated, and system-reserved.

Each permission represents **one atomic action**, for example:
- `participant.read`
- `participant.create`
- `participant.update`
- `participant.delete`
- `team.read`
- `team.create`
- `attendance.mark`
- `ticket.send`
- `email.send_bulk`
- `csv.import`
- `event.configure`
- `role.manage`
- `permission.view`

#### Key Rules
- Permissions are:
  - **Auto-generated by the system**
  - **Non-deletable**
  - **Non-editable**
- Only **roles** reference permissions
- Prevents permission drift and accidental privilege escalation

---

### 19.3 Permission Chunks (Feature-Based Grouping)

For UI and clarity, permissions are grouped into **feature chunks**, such as:

#### Participants
- `participant.read`
- `participant.create`
- `participant.update`
- `participant.delete`

#### Teams
- `team.read`
- `team.create`
- `team.update`
- `team.delete`

#### Attendance
- `attendance.read`
- `attendance.mark`

#### Tickets
- `ticket.read`
- `ticket.generate`
- `ticket.send`

#### Emails
- `email.read_logs`
- `email.send_bulk`

#### CSV Import
- `csv.import`

#### Events
- `event.read`
- `event.create`
- `event.update`
- `event.delete`
- `event.configure`

#### Roles & Security
- `role.read`
- `role.create`
- `role.update`
- `role.delete`
- `permission.read`

---

### 19.4 Backend Enforcement (Flask)

- Each protected endpoint declares required permission(s)
- Middleware checks:
  - Supabase JWT validity
  - User role
  - Role → permission mapping
- If missing permission → HTTP 403

Example:
- `/api/participants` (POST) → requires `participant.create`
- `/api/checkin/confirm` → requires `attendance.mark`

---

### 19.5 Super Admin Capabilities

Super Admin can:
- Create, edit, delete **roles**
- Assign **multiple permissions** to a role (multi-select UI)
- Assign roles to admin users
- View all system permissions (read-only)
- Override event-level restrictions if needed

Super Admin is **not permission-limited** and bypasses checks.

---

### 19.6 Admin Panel – Permission Management UI

#### Permissions Page
- Read-only list of:
  - Permission key
  - Description
  - Feature group
- No edit/delete options

#### Role Management Page
- Create new role
- Multi-select permissions (grouped by feature)
- Edit role permissions
- Delete role (if not in use)

#### Admin Assignment
- Assign role to admin / booth manager
- Changes apply immediately

---

### 19.7 Why This Design

- Prevents overpowered booth managers
- Scales cleanly as features grow
- Permissions stay consistent across events
- Matches enterprise-grade RBAC patterns
- Easy to audit and reason about

---

### 19.8 Default Roles (Seeded)

- **Super Admin**
  - All permissions (implicit)
- **Event Admin**
  - Full event + participant + ticket access
- **Booth Manager**
  - `participant.read`
  - `attendance.read`
  - `attendance.mark`

---

## 20. Deployment Checklist

### Pre-Deployment

#### Environment Setup
- [ ] Set up PostgreSQL database (or MySQL if preferred)
- [ ] Install Redis for Celery broker
- [ ] Configure Supabase Auth project
- [ ] Generate secure `SECRET_KEY` for Flask
- [ ] Set up SMTP credentials (test email delivery)
- [ ] Create `.env` file with all required variables

#### Environment Variables (.env)
```env
# Flask
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/event_dashboard
# OR for MySQL: mysql://user:password@localhost:3306/event_dashboard

# Redis (Celery)
REDIS_URL=redis://localhost:6379/0

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Event Management System

# Application
APP_URL=https://yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com

# Super Admin (optional, CLI recommended)
# SUPER_ADMIN_EMAIL=admin@example.com
# SUPER_ADMIN_NAME=Admin Name
# SUPER_ADMIN_PASSWORD=secure_password
```

#### Docker Setup
- [ ] Create `Dockerfile` for Flask app
- [ ] Create `docker-compose.yml` with:
  - Flask app
  - PostgreSQL
  - Redis
  - Celery worker
  - Celery beat (optional, for scheduled tasks)
- [ ] Build and test containers locally

#### Security Hardening
- [ ] Generate strong SECRET_KEY (use `secrets.token_hex(32)`)
- [ ] Configure CORS properly (whitelist domains only)
- [ ] Set up HTTPS with Let's Encrypt (via Certbot or Cloudflare)
- [ ] Enable HSTS headers
- [ ] Configure CSP (Content Security Policy) headers
- [ ] Set secure cookie flags (HttpOnly, Secure, SameSite)
- [ ] Review and limit API rate limits
- [ ] Set up WAF (Web Application Firewall) if using Cloudflare

### Deployment

#### Server Setup
- [ ] Provision server (VPS/cloud instance)
- [ ] Install Docker and Docker Compose
- [ ] Configure firewall (UFW/iptables):
  - Allow 80 (HTTP)
  - Allow 443 (HTTPS)
  - Allow 22 (SSH, restricted to your IP)
  - Deny all other incoming
- [ ] Set up SSH key authentication (disable password auth)
- [ ] Create non-root user for deployment

#### Nginx Configuration
- [ ] Install Nginx (or use Nginx Docker container)
- [ ] Configure reverse proxy to Flask app
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Enable gzip compression
- [ ] Configure rate limiting
- [ ] Set up static file serving (for CSS/JS)
- [ ] Configure Cloudflare Tunnel (if using)

Example Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/app/static;
        expires 30d;
    }
}
```

#### Application Deployment
- [ ] Clone repository to server
- [ ] Copy `.env` file to server (never commit to git!)
- [ ] Run database migrations:
  ```bash
  flask db upgrade
  ```
- [ ] Seed permissions and default roles:
  ```bash
  flask seed-permissions
  flask seed-roles
  ```
- [ ] Create Super Admin:
  ```bash
  flask create-super-admin --email admin@example.com --name "Admin Name"
  ```
- [ ] Start services:
  ```bash
  docker-compose up -d
  ```

#### Celery Workers
- [ ] Configure Celery worker count (based on server resources)
- [ ] Set up Celery beat for scheduled tasks (if needed)
- [ ] Configure worker auto-restart on failure
- [ ] Set up log rotation for Celery logs

### Post-Deployment

#### Monitoring & Logging
- [ ] Set up application monitoring (Sentry for errors)
- [ ] Configure uptime monitoring (UptimeRobot, Pingdom)
- [ ] Set up log aggregation (ELK stack, or simple log files)
- [ ] Enable Flask logging to file
- [ ] Configure Celery logging
- [ ] Set up PostgreSQL slow query logging
- [ ] Monitor Redis memory usage

#### Backup Strategy
- [ ] Automated daily database backups:
  ```bash
  pg_dump -U user event_dashboard > backup_$(date +%Y%m%d).sql
  ```
- [ ] Store backups off-site (S3, Backblaze B2)
- [ ] Test backup restoration monthly
- [ ] Back up uploaded files (if any)
- [ ] Back up `.env` file securely

#### Performance Optimization
- [ ] Enable PostgreSQL query caching
- [ ] Configure Redis cache for frequent queries
- [ ] Set up CDN for static assets (Cloudflare)
- [ ] Enable database connection pooling
- [ ] Configure Gunicorn workers (2-4 × CPU cores)
- [ ] Set up database indexing on frequently queried columns

#### Testing Production
- [ ] Test CSV import with 500+ rows
- [ ] Test bulk email sending
- [ ] Test PDF generation performance
- [ ] Test QR scanner on mobile devices
- [ ] Verify HTTPS is enforced
- [ ] Test authentication flow
- [ ] Verify email delivery (check spam folders)
- [ ] Load test with expected concurrent users

### Maintenance

#### Regular Tasks
- [ ] Weekly security updates (OS, Docker images)
- [ ] Monthly backup restoration test
- [ ] Review error logs weekly
- [ ] Monitor disk space usage
- [ ] Review and rotate logs
- [ ] Update dependencies (pip packages)
- [ ] Review failed email queue

#### Emergency Procedures
- [ ] Document rollback procedure
- [ ] Keep previous Docker images tagged
- [ ] Maintain emergency contact list
- [ ] Document database restore process
- [ ] Set up status page (for public updates during incidents)

### Security Checklist
- [ ] All secrets in environment variables (not in code)
- [ ] Database credentials are strong and unique
- [ ] Supabase RLS policies configured correctly
- [ ] API endpoints require authentication
- [ ] CSRF protection enabled on forms
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection (template escaping)
- [ ] Rate limiting on all public endpoints
- [ ] File upload restrictions (if applicable)
- [ ] Regular security audits

### Optional: Advanced Setup
- [ ] Set up CI/CD pipeline (GitHub Actions, GitLab CI)
- [ ] Configure auto-scaling (if using cloud)
- [ ] Set up multi-region deployment (for redundancy)
- [ ] Implement blue-green deployment
- [ ] Set up staging environment
- [ ] Configure A/B testing infrastructure

---

## 21. Islamic Context Integration (Optional Feature)

### Prayer Time Integration
The `schedule_config` (JSONB) field in the events table can store:

```json
{
  "prayer_times": {
    "fajr": "05:30",
    "zuhr": "13:15",
    "asr": "17:20",
    "maghrib": "18:50",
    "esha": "20:30"
  },
  "breaks": [
    {"name": "Zuhr Prayer Break", "start": "13:15", "duration": 30},
    {"name": "Asr Prayer Break", "start": "17:20", "duration": 20}
  ]
}
```

**Use cases:**
- Display prayer times on tickets
- Event timeline respects prayer breaks
- Auto-schedule sessions around prayer times
- Send reminder notifications before each prayer

### Halal Dietary Preferences
The `custom_fields` can include:

```json
{
  "fields": [
    {"name": "dietary_preference", "type": "select", "options": ["Halal", "Vegetarian", "Vegan", "No Preference"]},
    {"name": "allergies", "type": "text"},
    {"name": "emergency_contact", "type": "text"}
  ]
}
```

**Why this matters:**
- Ensures halal catering for Muslim attendees
- Tracks dietary needs for community iftars or events
- Respects Islamic food requirements

### Gender-Segregated Events
Add a custom field:

```json
{"name": "section", "type": "select", "options": ["Brothers", "Sisters", "Family"]}
```

**Use cases:**
- Separate check-in counters for brothers/sisters
- Seating arrangements
- Team assignments (brothers-only or sisters-only teams)
- Privacy-conscious reporting

### Mahram Information (If Needed)
For events requiring mahram documentation:

```json
{"name": "mahram_name", "type": "text"},
{"name": "mahram_relationship", "type": "select", "options": ["Father", "Brother", "Husband", "Uncle"]}
```

### Islamic Calendar Integration
- Store event dates in both Gregorian and Hijri
- Display Hijri date on tickets (e.g., "15 Ramadan 1447")
- Tag events by Islamic season (Ramadan, Dhul Hijjah, etc.)

### Donation/Sadaqah Tracking
If events involve fundraising:

```json
{"name": "donation_amount", "type": "number"},
{"name": "donation_cause", "type": "select", "options": ["Masjid Fund", "Zakat", "General Sadaqah"]}
```

### Practical Example: Ramadan Iftar Event

```json
{
  "event_name": "Community Iftar 2026",
  "mode": "solo",
  "schedule_config": {
    "prayer_times": {"maghrib": "18:45", "esha": "20:30"},
    "program": [
      {"time": "18:30", "activity": "Arrival & Registration"},
      {"time": "18:45", "activity": "Maghrib Adhan & Iftar"},
      {"time": "19:30", "activity": "Maghrib Prayer"},
      {"time": "19:50", "activity": "Lecture: Ramadan Reflections"},
      {"time": "20:30", "activity": "Esha Prayer & Departure"}
    ]
  },
  "custom_fields": [
    {"name": "dietary_preference", "options": ["Halal", "Vegetarian"]},
    {"name": "section", "options": ["Brothers", "Sisters", "Family"]},
    {"name": "volunteer_interest", "type": "checkbox"}
  ]
}
```

**Ticket Output Example:**
```
بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

Community Iftar 2026
Saturday, 15 Ramadan 1447 | March 15, 2026

Registration: 6:30 PM
Iftar: 6:45 PM (Maghrib)
Prayer Times: Maghrib 6:45 PM | Esha 8:30 PM

Dietary: Halal
Section: Brothers

[QR CODE]

JazakAllahu Khairan for registering!
```

---

```mermaid
graph TB
    subgraph "External Services"
        SUPABASE[Supabase Auth<br/>JWT Validation]
        SMTP[SMTP Server<br/>Email Delivery]
    end

    subgraph "Frontend Layer"
        ADMIN_UI[Admin Panel<br/>TailwindCSS + DaisyUI]
        SCANNER[QR Scanner Page<br/>Alpine.js + Camera API]
        TICKET_VIEW[Ticket View Page<br/>Public Access]
    end

    subgraph "Flask Backend"
        API[Flask API<br/>REST Endpoints]
        AUTH_MW[Auth Middleware<br/>JWT + RBAC]
        
        subgraph "Core Services"
            EVENT_SVC[Event Service]
            PARTICIPANT_SVC[Participant Service]
            TEAM_SVC[Team Service]
            CHECKIN_SVC[Check-in Service]
            EMAIL_SVC[Email Service]
            TICKET_SVC[Ticket Service]
            ROLE_SVC[Role & Permission Service]
        end
    end

    subgraph "Background Jobs - Celery"
        CELERY_WORKER[Celery Workers]
        CSV_JOB[CSV Import Job]
        EMAIL_JOB[Bulk Email Job]
        PDF_JOB[PDF Generation Job]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL<br/>Main Database)]
        REDIS[(Redis<br/>Celery Broker)]
        
        subgraph "Database Tables"
            EVENTS[events]
            TEAMS[teams<br/>is_empty flag]
            PARTICIPANTS[participants<br/>custom_data JSONB]
            EMAIL_LOGS[email_logs<br/>retry logic]
            CHECKIN_LOGS[checkin_logs<br/>audit trail]
            ROLES[roles]
            PERMISSIONS[permissions]
            ROLE_PERMS[role_permissions]
            ADMIN_USERS[admin_users]
            CELERY_JOBS[celery_jobs<br/>progress tracking]
        end
    end

    subgraph "File Generation"
        WEASYPRINT[WeasyPrint<br/>PDF Engine]
        QR_GEN[QR Code Generator<br/>segno/qrcode]
    end

    %% Frontend to Backend
    ADMIN_UI -->|HTTP/HTTPS| API
    SCANNER -->|HTTP/HTTPS| API
    TICKET_VIEW -->|HTTP/HTTPS| API

    %% Backend to External
    API -->|Validate JWT| SUPABASE
    EMAIL_SVC -->|Send Emails| SMTP

    %% API to Middleware
    API --> AUTH_MW

    %% Middleware to Services
    AUTH_MW --> EVENT_SVC
    AUTH_MW --> PARTICIPANT_SVC
    AUTH_MW --> TEAM_SVC
    AUTH_MW --> CHECKIN_SVC
    AUTH_MW --> EMAIL_SVC
    AUTH_MW --> TICKET_SVC
    AUTH_MW --> ROLE_SVC

    %% Services to Database
    EVENT_SVC --> EVENTS
    PARTICIPANT_SVC --> PARTICIPANTS
    TEAM_SVC --> TEAMS
    CHECKIN_SVC --> CHECKIN_LOGS
    EMAIL_SVC --> EMAIL_LOGS
    ROLE_SVC --> ROLES
    ROLE_SVC --> PERMISSIONS
    ROLE_SVC --> ROLE_PERMS
    ROLE_SVC --> ADMIN_USERS

    %% Services to Celery
    PARTICIPANT_SVC -.Queue Job.-> REDIS
    EMAIL_SVC -.Queue Job.-> REDIS
    TICKET_SVC -.Queue Job.-> REDIS

    %% Celery Workers
    REDIS --> CELERY_WORKER
    CELERY_WORKER --> CSV_JOB
    CELERY_WORKER --> EMAIL_JOB
    CELERY_WORKER --> PDF_JOB

    %% Jobs to Database
    CSV_JOB --> PARTICIPANTS
    CSV_JOB --> TEAMS
    EMAIL_JOB --> EMAIL_LOGS
    PDF_JOB --> CELERY_JOBS

    %% Jobs to File Generation
    EMAIL_JOB --> SMTP
    PDF_JOB --> WEASYPRINT
    PDF_JOB --> QR_GEN

    %% File Generation to Services
    WEASYPRINT --> TICKET_SVC
    QR_GEN --> TICKET_SVC

    %% All Services to Postgres
    EVENT_SVC --> POSTGRES
    PARTICIPANT_SVC --> POSTGRES
    TEAM_SVC --> POSTGRES
    CHECKIN_SVC --> POSTGRES
    EMAIL_SVC --> POSTGRES
    TICKET_SVC --> POSTGRES
    ROLE_SVC --> POSTGRES

    %% Jobs to Postgres
    CSV_JOB --> POSTGRES
    EMAIL_JOB --> POSTGRES
    PDF_JOB --> POSTGRES

    style SUPABASE fill:#10b981
    style SMTP fill:#10b981
    style POSTGRES fill:#3b82f6
    style REDIS fill:#ef4444
    style CELERY_WORKER fill:#f59e0b
    style API fill:#8b5cf6
    style AUTH_MW fill:#ec4899
```
Built for chaos. Designed for real events.
