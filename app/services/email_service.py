"""
Email service for sending emails via SMTP
"""
from flask import current_app
from flask_mail import Message
from app.app import mail
from app.models import db
from app.models.events import EmailLog
from datetime import datetime


def send_email(recipient, subject, body, html=None):
    """Send a single email"""
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body,
            html=html
        )
        mail.send(msg)
        return True, None
    except Exception as e:
        return False, str(e)


def send_bulk_emails(event_id, subject, template_name, recipients):
    """Send bulk emails to multiple recipients"""
    from app.app import create_app
    app = create_app()
    
    with app.app_context():
        success_count = 0
        failed_count = 0
        
        for recipient in recipients:
            # Create email log
            email_log = EmailLog(
                event_id=event_id,
                recipient_email=recipient['email'],
                subject=subject,
                template_name=template_name,
                status='queued'
            )
            db.session.add(email_log)
            db.session.flush()
            
            # Render email template
            # TODO: Implement template rendering with participant data
            body = f"Hello {recipient.get('name', 'Participant')},\n\nYour ticket for the event."
            html = f"<p>Hello {recipient.get('name', 'Participant')},</p><p>Your ticket for the event.</p>"
            
            # Send email
            success, error = send_email(recipient['email'], subject, body, html)
            
            if success:
                email_log.status = 'sent'
                email_log.sent_at = datetime.utcnow()
                success_count += 1
            else:
                email_log.status = 'failed'
                email_log.error_message = error
                failed_count += 1
            
            db.session.commit()
        
        return {
            'success': True,
            'success_count': success_count,
            'failed_count': failed_count
        }


def retry_failed_emails(event_id):
    """Retry failed email deliveries"""
    from app.app import create_app
    app = create_app()
    
    with app.app_context():
        failed_emails = EmailLog.query.filter_by(
            event_id=event_id,
            status='failed'
        ).filter(
            EmailLog.retry_count < 3
        ).all()
        
        retried_count = 0
        
        for email_log in failed_emails:
            # TODO: Get participant data and render template
            body = "Retry email body"
            html = "<p>Retry email body</p>"
            
            success, error = send_email(
                email_log.recipient_email,
                email_log.subject,
                body,
                html
            )
            
            if success:
                email_log.status = 'sent'
                email_log.sent_at = datetime.utcnow()
                retried_count += 1
            else:
                email_log.retry_count += 1
                email_log.error_message = error
            
            db.session.commit()
        
        return {
            'success': True,
            'retried_count': retried_count
        }
