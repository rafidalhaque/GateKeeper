"""
Celery application configuration
"""
from celery import Celery
from celery.signals import worker_process_init
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
)

# Global Flask app instance for workers
flask_app = None


@worker_process_init.connect
def init_worker_process(sender=None, **kwargs):
    """Initialize Flask app context when worker process starts"""
    global flask_app
    from app.app import create_app
    
    flask_app = create_app()
    # Push app context for this worker process
    flask_app.app_context().push()


# Update base Task class to use Flask app context
class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context"""
    def __call__(self, *args, **kwargs):
        # Context is already pushed in worker_process_init
        # Just run the task
        return self.run(*args, **kwargs)

celery.Task = ContextTask


# Import tasks to register them with Celery (after celery instance is created)
from app.services import tasks  # noqa: E402, F401
