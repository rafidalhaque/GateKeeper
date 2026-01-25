# GateKeeper

**Self-hosted Onsite Event Access Platform**

GateKeeper is a comprehensive event management system designed for real-world events with features like QR-based attendance, ticketing with PDF delivery, team management, role-based access control, and background job processing.

## Features

### Core Capabilities
- ✅ **Event Management** - Create and manage solo or team-based events
- ✅ **QR-Based Attendance** - Fast check-in with QR code scanning
- ✅ **Ticketing System** - PDF ticket generation with custom templates
- ✅ **Email Delivery** - Bulk email sending with retry logic
- ✅ **CSV Import** - Bulk participant import with background processing
- ✅ **Team Management** - Complete team lifecycle with auto-flagging of empty teams
- ✅ **Role-Based Access Control (RBAC)** - Granular permission system
- ✅ **Real-time Reports** - Attendance analytics and export

### Authentication & Security
- Supabase JWT authentication
- Permission-based access control
- Audit logging for all check-ins
- Secure UUID-based ticket URLs
- HTTPS support with secure cookies

### Background Jobs
- Celery-based job queue
- Email sending with retry mechanism
- PDF ticket generation
- CSV import processing
- Real-time progress tracking

## Tech Stack

### Backend
- **Python 3.10+** with Flask
- **SQLAlchemy** ORM
- **PostgreSQL** (recommended) or MySQL
- **Celery** for background jobs
- **Redis** for job queue and caching
- **WeasyPrint** for PDF generation

### Frontend
- **TailwindCSS** + DaisyUI for styling
- **Alpine.js** for interactivity
- **Jinja2** templates
- Browser Camera API for QR scanning

### Infrastructure
- **Docker** and Docker Compose
- **Nginx** reverse proxy
- **Supabase** for authentication

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rafidalhaque/GateKeeper.git
   cd GateKeeper
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec web flask db upgrade
   ```

5. **Seed permissions and roles**
   ```bash
   docker-compose exec web flask seed-permissions
   docker-compose exec web flask seed-roles
   ```

6. **Create super admin**
   ```bash
   docker-compose exec web flask create-super-admin
   ```

7. **Access the application**
   - Web: http://localhost:5000
   - API: http://localhost:5000/api

## Configuration

### Environment Variables

Key configuration variables (see `.env.example` for full list):

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gatekeeper

# Redis
REDIS_URL=redis://localhost:6379/0

# Supabase Authentication
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
APP_URL=http://localhost:5000
SECRET_KEY=generate-a-secure-key-here
```

## API Documentation

### Events
- `POST /api/events` - Create event
- `GET /api/events` - List events
- `GET /api/events/<id>` - Get event details
- `PUT /api/events/<id>` - Update event
- `DELETE /api/events/<id>` - Delete event

### Participants
- `POST /api/participants` - Create participant
- `GET /api/participants?event_id=<id>` - List participants
- `PUT /api/participants/<id>` - Update participant
- `DELETE /api/participants/<id>` - Delete participant

### Check-in
- `GET /api/checkin/lookup/<uuid>` - Lookup participant
- `POST /api/checkin/confirm` - Confirm check-in
- `GET /api/checkin/logs?event_id=<id>` - Get check-in logs

### Reports
- `GET /api/reports/attendance-summary?event_id=<id>` - Attendance stats
- `GET /api/reports/export-csv?event_id=<id>` - Export CSV
- `GET /api/reports/team-stats?event_id=<id>` - Team statistics

See [plan.md](docs/plan.md) for complete API documentation.

## Development

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up local database**
   ```bash
   # Using PostgreSQL
   createdb gatekeeper
   
   # Update .env with local database URL
   DATABASE_URL=postgresql://user:password@localhost:5432/gatekeeper
   ```

4. **Run migrations**
   ```bash
   flask db upgrade
   flask seed-permissions
   flask seed-roles
   ```

5. **Start Redis**
   ```bash
   redis-server
   ```

6. **Start Celery worker**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

7. **Run Flask development server**
   ```bash
   flask run
   ```

## Deployment

See the [Deployment Checklist](docs/plan.md#20-deployment-checklist) in plan.md for comprehensive deployment instructions including:
- Server setup
- Nginx configuration
- SSL/TLS setup
- Security hardening
- Monitoring and backups

## Project Structure

```
GateKeeper/
├── app/
│   ├── models/          # Database models
│   │   ├── events.py    # Event, Participant, Team models
│   │   └── auth.py      # RBAC models
│   ├── routes/          # API endpoints
│   │   ├── events.py
│   │   ├── participants.py
│   │   ├── teams.py
│   │   ├── checkin.py
│   │   ├── tickets.py
│   │   ├── emails.py
│   │   ├── admin.py
│   │   └── reports.py
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   │   ├── auth.py      # Authentication helpers
│   │   └── errors.py    # Error handlers
│   ├── templates/       # HTML templates
│   ├── static/          # Static assets
│   ├── app.py           # App factory
│   ├── config.py        # Configuration
│   └── cli.py           # CLI commands
├── migrations/          # Database migrations
├── docker-compose.yml   # Docker services
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── run.py              # Application entry point
```

## Role-Based Access Control

### Default Roles

1. **Super Admin** - Full system access
2. **Event Admin** - Full event and participant management
3. **Booth Manager** - Check-in operations only

### Permissions

Permissions are organized by feature groups:
- **Participants**: read, create, update, delete
- **Teams**: read, create, update, delete
- **Attendance**: read, mark
- **Tickets**: read, generate, send
- **Emails**: read_logs, send_bulk
- **Events**: read, create, update, delete, configure
- **Roles**: read, create, update, delete
- **Reports**: read, export

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please use the GitHub issue tracker.

## Contributing

Contributions are welcome! Please read the contribution guidelines before submitting pull requests.

---

**Built for chaos. Designed for real events.**
