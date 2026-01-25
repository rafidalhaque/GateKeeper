"""
Celery application configuration
"""
from celery import Celery
from app.config import Config

# Create Celery instance first (without Flask app to avoid circular imports)
celery = Celery(
    'gatekeeper',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)

celery.conf.update(
    task_serializer=Config.CELERY_TASK_SERIALIZER,
    result_serializer=Config.CELERY_RESULT_SERIALIZER,
    accept_content=Config.CELERY_ACCEPT_CONTENT,
    timezone=Config.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_always_eager=False,
)


# Update base Task class to use Flask app context
class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context"""
    def __call__(self, *args, **kwargs):
        from app.app import create_app

        # Create Flask app and push context for each task call
        app = create_app()
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


# Import tasks to register them with Celery (after celery instance is created)
from app.services import tasks  # noqa: E402, F401
