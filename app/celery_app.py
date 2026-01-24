"""
Celery application configuration
"""
from celery import Celery
from app.config import Config

def make_celery():
    """Create and configure Celery instance"""
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
    
    return celery

celery = make_celery()

# Import tasks to register them with Celery
from app.services import tasks
