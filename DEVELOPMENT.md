# Development Guide

Guide for developers working on GateKeeper.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 15+ or MySQL 8+
- Redis 7+
- Node.js (for TailwindCSS, optional)
- Git

### Local Setup

1. **Clone the repository**

```bash
git clone https://github.com/rafidalhaque/GateKeeper.git
cd GateKeeper
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up local database**

```bash
# PostgreSQL
createdb gatekeeper

# Or MySQL
mysql -u root -p -e "CREATE DATABASE gatekeeper;"
```

5. **Configure environment**

```bash
cp .env.example .env
# Edit .env with local database credentials
```

6. **Run migrations**

```bash
flask db upgrade
```

7. **Seed data**

```bash
flask seed-permissions
flask seed-roles
flask create-super-admin --email admin@local.test --name "Local Admin"
```

8. **Start services**

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery worker
celery -A app.celery_app worker --loglevel=info

# Terminal 3: Flask app
flask run
```

Visit http://localhost:5000

## Project Structure

```
GateKeeper/
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask app factory
│   ├── celery_app.py       # Celery configuration
│   ├── cli.py              # CLI commands
│   ├── config.py           # Configuration
│   │
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   ├── auth.py         # RBAC models
│   │   └── events.py       # Event models
│   │
│   ├── routes/             # API routes/blueprints
│   │   ├── __init__.py
│   │   ├── admin.py        # Admin/RBAC routes
│   │   ├── checkin.py      # Check-in routes
│   │   ├── csv_import.py   # CSV import
│   │   ├── emails.py       # Email routes
│   │   ├── events.py       # Event management
│   │   ├── frontend.py     # Frontend routes
│   │   ├── participants.py # Participant management
│   │   ├── reports.py      # Reports & analytics
│   │   ├── teams.py        # Team management
│   │   └── tickets.py      # Ticket generation
│   │
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── csv_import.py   # CSV processing
│   │   ├── email_service.py # Email sending
│   │   ├── tasks.py        # Celery tasks
│   │   └── ticket_service.py # PDF generation
│   │
│   ├── utils/              # Utilities
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication
│   │   ├── errors.py       # Error handlers
│   │   ├── security.py     # Security utilities
│   │   └── validation.py   # Input validation
│   │
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html
│   │   ├── scanner.html
│   │   └── ticket.html
│   │
│   └── static/             # Static files
│       ├── css/
│       └── js/
│
├── migrations/             # Database migrations
├── examples/               # Example files
├── tests/                  # Tests (to be added)
│
├── .env.example            # Environment template
├── .gitignore
├── API.md                  # API documentation
├── CONTRIBUTING.md         # Contribution guide
├── DEPLOYMENT.md           # Deployment guide
├── docker-compose.yml
├── Dockerfile
├── plan.md                 # System design
├── README.md
├── requirements.txt
└── run.py                  # Entry point
```

## Database Migrations

### Create Migration

```bash
# Auto-generate migration
flask db migrate -m "Description of changes"

# Review the generated migration in migrations/versions/

# Apply migration
flask db upgrade
```

### Manual Migration

```bash
# Create empty migration
flask db revision -m "Manual migration"

# Edit the file in migrations/versions/
# Add upgrade() and downgrade() functions

# Apply
flask db upgrade
```

### Rollback

```bash
# Rollback one version
flask db downgrade

# Rollback to specific version
flask db downgrade <revision>
```

## Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_events.py

# Run specific test
pytest tests/test_events.py::test_create_event
```

### Write Tests

Create test files in `tests/` directory:

```python
# tests/test_events.py
import pytest
from app.app import create_app
from app.models import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_event(client):
    response = client.post('/api/events', json={
        'name': 'Test Event',
        'date': '2024-12-01T09:00:00Z',
        'mode': 'solo'
    })
    assert response.status_code == 201
```

## Code Style

### Python Style Guide

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use double quotes for strings
- Add docstrings to all functions/classes

### Example

```python
"""
Module docstring explaining purpose
"""
from typing import Optional

def process_participant(participant_id: str, event_id: str) -> Optional[dict]:
    """
    Process participant data for an event.
    
    Args:
        participant_id: UUID of the participant
        event_id: UUID of the event
        
    Returns:
        Dictionary with participant data, or None if not found
    """
    # Implementation
    pass
```

### Format Code

```bash
# Install formatters
pip install black isort

# Format code
black app/
isort app/

# Check without modifying
black --check app/
```

## Debugging

### Flask Shell

```bash
flask shell
```

```python
# In shell
from app.models import db
from app.models.events import Event, Participant

# Query data
events = Event.query.all()
participant = Participant.query.first()

# Create data
event = Event(name="Debug Event", mode="solo")
db.session.add(event)
db.session.commit()
```

### VSCode Debug Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "run.py",
        "FLASK_ENV": "development"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true
    }
  ]
}
```

### Logging

```python
from flask import current_app

# In routes or services
current_app.logger.info("Processing event")
current_app.logger.error("Error occurred", exc_info=True)
current_app.logger.debug("Debug information")
```

## Common Tasks

### Add New API Endpoint

1. Create route in appropriate blueprint
2. Add permission check
3. Implement validation
4. Add tests
5. Update API.md

Example:

```python
# app/routes/events.py
@bp.route('/<uuid:event_id>/statistics', methods=['GET'])
@permission_required('event.read')
def get_event_statistics(event_id):
    """Get event statistics"""
    event = Event.query.get_or_404(event_id)
    
    # Implementation
    
    return jsonify(statistics)
```

### Add New Permission

1. Add to `app/cli.py` in `seed_permissions()`
2. Run `flask seed-permissions`
3. Assign to appropriate roles

### Add New Celery Task

1. Create task in `app/services/tasks.py`
2. Implement task logic in service module
3. Add job tracking
4. Test with `task.delay()`

### Add New Model Field

1. Add field to model in `app/models/`
2. Create migration: `flask db migrate`
3. Review and apply: `flask db upgrade`
4. Update API responses

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### Commit Messages

```
type: brief description

Longer explanation if needed

- Change 1
- Change 2

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. Create feature branch
2. Make changes and commit
3. Push to fork
4. Create PR with description
5. Address review feedback
6. Merge when approved

## Performance Tips

### Database Queries

```python
# Bad: N+1 queries
participants = Participant.query.all()
for p in participants:
    print(p.team.name)  # Separate query for each

# Good: Eager loading
participants = Participant.query.options(
    db.joinedload(Participant.team)
).all()
for p in participants:
    print(p.team.name)  # Already loaded
```

### Pagination

```python
# For large result sets
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 20, type=int)

participants = Participant.query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)

return jsonify({
    'items': [p.to_dict() for p in participants.items],
    'total': participants.total,
    'pages': participants.pages,
    'current_page': page
})
```

### Caching

```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_event_statistics(event_id):
    # Expensive computation
    return statistics
```

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Alpine.js Documentation](https://alpinejs.dev/)

## Getting Help

- Check existing issues on GitHub
- Review documentation and guides
- Ask in discussions
- Contact maintainers

Happy coding! 🚀
