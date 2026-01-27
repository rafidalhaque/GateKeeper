#!/usr/bin/env python
"""
Celery Worker Entry Point
Run with: celery -A celery_worker worker --loglevel=info --pool=solo
"""
import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import celery app
from app.celery_app import celery

# Import tasks to register them
from app.services import tasks  # noqa: F401

if __name__ == '__main__':
    celery.start()
