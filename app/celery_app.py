"""
Celery application configuration
"""
from celery import Celery
from app.config import Config

def make_celery(app_name='gatekeeper'):
    """Create and configure Celery instance"""
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.services.tasks']
    )

    # Update configuration
    celery.conf.update(
        task_serializer=Config.CELERY_TASK_SERIALIZER,
        result_serializer=Config.CELERY_RESULT_SERIALIZER,
        accept_content=Config.CELERY_ACCEPT_CONTENT,
        timezone=Config.CELERY_TIMEZONE,
        enable_utc=True,
        task_track_started=False,
        task_ignore_result=False,
        result_expires=3600,
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
        worker_pool='solo',  # Use solo pool for Windows compatibility
    )

    # Create context task
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            from app.app import create_app
            app = create_app()
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery

# Create the celery instance
celery = make_celery()


