"""
Celery background tasks
"""
from app.celery_app import celery
from app.models import db
from app.models.events import CeleryJob
from datetime import datetime
import uuid


@celery.task(bind=True)
def import_csv_task(self, event_id, csv_content):
    """Background task for CSV import"""
    from app.services.csv_import import process_csv_import
    
    # Create job tracking record
    job = CeleryJob(
        task_name='import_csv',
        task_id=self.request.id,
        status='processing',
        started_at=datetime.utcnow()
    )
    db.session.add(job)
    db.session.commit()
    
    try:
        # Process CSV
        result = process_csv_import(event_id, csv_content)
        
        # Update job status
        job.status = 'completed' if result['success'] else 'failed'
        job.progress = 100
        job.completed_at = datetime.utcnow()
        
        if not result['success']:
            job.error_message = result.get('error', 'Unknown error')
        
        db.session.commit()
        
        return result
    
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        raise


@celery.task(bind=True)
def send_bulk_emails_task(self, event_id, subject, template_name, recipients):
    """Background task for bulk email sending"""
    from app.services.email_service import send_bulk_emails
    
    # Create job tracking record
    job = CeleryJob(
        task_name='send_bulk_emails',
        task_id=self.request.id,
        status='processing',
        total_items=len(recipients),
        started_at=datetime.utcnow()
    )
    db.session.add(job)
    db.session.commit()
    
    try:
        # Send emails
        result = send_bulk_emails(event_id, subject, template_name, recipients)
        
        # Update job status
        job.status = 'completed'
        job.progress = 100
        job.processed_items = result['success_count']
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        return result
    
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        raise


@celery.task(bind=True)
def generate_tickets_task(self, event_id):
    """Background task for ticket generation"""
    from app.services.ticket_service import generate_bulk_tickets
    
    # Create job tracking record
    job = CeleryJob(
        task_name='generate_tickets',
        task_id=self.request.id,
        status='processing',
        started_at=datetime.utcnow()
    )
    db.session.add(job)
    db.session.commit()
    
    try:
        # Generate tickets
        result = generate_bulk_tickets(event_id)
        
        # Update job status
        job.status = 'completed' if result['success'] else 'failed'
        job.progress = 100
        job.processed_items = result['generated_count']
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        return result
    
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.session.commit()
        
        raise
