"""
Email service for sending emails via SMTP
"""
from flask import current_app
from flask_mail import Message
from app.app import mail
from app.models import db
from app.models.events import EmailLog
from app.models.auth import SMTPConfig
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_smtp_config():
    """Get SMTP configuration from database, fallback to .env"""
    # Try to get from database first (supersedes .env)
    db_config = SMTPConfig.query.filter_by(is_active=True).first()

    if db_config:
        return {
            'server': db_config.smtp_server,
            'port': db_config.smtp_port,
            'username': db_config.smtp_username,
            'password': db_config.smtp_password,
            'use_tls': db_config.smtp_use_tls,
            'use_ssl': db_config.smtp_use_ssl,
            'sender_email': db_config.sender_email,
            'sender_name': db_config.sender_name,
            'from_db': True
        }

    # Fallback to .env configuration
    return {
        'server': current_app.config.get('MAIL_SERVER'),
        'port': current_app.config.get('MAIL_PORT', 587),
        'username': current_app.config.get('MAIL_USERNAME'),
        'password': current_app.config.get('MAIL_PASSWORD'),
        'use_tls': current_app.config.get('MAIL_USE_TLS', True),
        'use_ssl': current_app.config.get('MAIL_USE_SSL', False),
        'sender_email': current_app.config.get('MAIL_DEFAULT_SENDER'),
        'sender_name': current_app.config.get('MAIL_SENDER_NAME', 'GateKeeper'),
        'from_db': False
    }


def send_email_smtp(recipient, subject, body, html=None):
    """Send email using SMTP directly (supports both DB and .env config)"""
    config = get_smtp_config()

    try:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        message['To'] = recipient

        # Attach parts
        if body:
            part1 = MIMEText(body, 'plain')
            message.attach(part1)

        if html:
            part2 = MIMEText(html, 'html')
            message.attach(part2)

        # Connect and send
        if config['use_ssl']:
            server = smtplib.SMTP_SSL(config['server'], config['port'])
        else:
            server = smtplib.SMTP(config['server'], config['port'])
            if config['use_tls']:
                server.starttls()

        server.login(config['username'], config['password'])
        server.sendmail(config['sender_email'], recipient, message.as_string())
        server.quit()

        return True, None
    except Exception as e:
        return False, str(e)


def send_email(recipient, subject, body, html=None):
    """Send a single email (uses DB config if available, otherwise .env)"""
    return send_email_smtp(recipient, subject, body, html)


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
