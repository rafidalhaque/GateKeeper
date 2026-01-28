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
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import os


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


def send_email_smtp(recipient, subject, body, html=None, attachments=None, embedded_images=None):
    """
    Send email using SMTP directly (supports both DB and .env config)

    Args:
        recipient: Email address
        subject: Email subject
        body: Plain text body
        html: HTML body (optional)
        attachments: List of dicts with 'filename' and 'content' (bytes) for PDF/file attachments
        embedded_images: List of dicts with 'cid', 'filename', and 'content' (bytes) for inline images
    """
    config = get_smtp_config()

    try:
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From'] = f"{config['sender_name']} <{config['sender_email']}>"
        message['To'] = recipient

        # Create alternative part for text and HTML
        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)

        # Attach text part
        if body:
            part1 = MIMEText(body, 'plain')
            msg_alternative.attach(part1)

        # If we have embedded images, create related multipart
        if html and embedded_images:
            msg_related = MIMEMultipart('related')
            msg_alternative.attach(msg_related)

            # Attach HTML
            part2 = MIMEText(html, 'html')
            msg_related.attach(part2)

            # Attach embedded images
            for img in embedded_images:
                img_part = MIMEImage(img['content'])
                img_part.add_header('Content-ID', f"<{img['cid']}>")
                img_part.add_header('Content-Disposition', 'inline', filename=img['filename'])
                msg_related.attach(img_part)
        elif html:
            # Just attach HTML without embedded images
            part2 = MIMEText(html, 'html')
            msg_alternative.attach(part2)

        # Attach files (PDFs, etc.)
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment['content'])
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename= {attachment['filename']}"
                )
                message.attach(part)

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


def send_email(recipient, subject, body, html=None, attachments=None, embedded_images=None):
    """
    Send a single email (uses DB config if available, otherwise .env)

    Args:
        recipient: Email address
        subject: Email subject
        body: Plain text body
        html: HTML body (optional)
        attachments: List of dicts with 'filename' and 'content' for PDF/file attachments
        embedded_images: List of dicts with 'cid', 'filename', and 'content' for inline images
    """
    return send_email_smtp(recipient, subject, body, html, attachments, embedded_images)


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


def send_ticket_email(participant_id, template_id=None, attach_pdf=True):
    """
    Send ticket email to a participant with optional PDF attachment

    Args:
        participant_id: Participant ID
        template_id: Email template ID (optional, uses default ticket template)
        attach_pdf: Whether to attach PDF ticket (default: True)

    Returns:
        Tuple of (success: bool, error_message: str or None)
    """
    from app.models.events import Participant, EmailTemplate
    from app.services.ticket_service import generate_ticket_pdf
    from app.models.attachments import ImageAttachment
    from jinja2 import Template
    from pathlib import Path

    try:
        # Get participant and event
        participant = Participant.query.get(participant_id)
        if not participant:
            return False, "Participant not found"

        event = participant.event
        if not event:
            return False, "Event not found"

        # Get email template
        if template_id:
            email_template = EmailTemplate.query.get(template_id)
        else:
            # Use default ticket template
            email_template = EmailTemplate.query.filter_by(type='ticket').first()

        if not email_template:
            return False, "Email template not found"

        # Prepare template context
        context = {
            'participant': {
                'name': participant.name,
                'email': participant.email,
                'unique_url': f"{current_app.config.get('APP_URL', 'http://localhost:5000')}/ticket/{participant.unique_url_uuid}",
                'uuid': str(participant.unique_url_uuid)
            },
            'event': {
                'name': event.name,
                'date': event.date.strftime('%B %d, %Y'),
                'venue': event.venue or 'TBA',
                'mode': event.mode
            },
            'current_year': datetime.utcnow().year,
            'app_name': 'GateKeeper',
            'support_email': current_app.config.get('MAIL_DEFAULT_SENDER', 'support@example.com')
        }

        # Add team info if applicable
        if participant.team:
            context['team'] = {
                'name': participant.team.team_name,
                'id': participant.team.id
            }

        # Add custom fields
        if participant.custom_data:
            context['custom_fields'] = participant.custom_data

        # Render subject
        subject_template = Template(email_template.subject)
        subject = subject_template.render(**context)

        # Render HTML content
        html_template = Template(email_template.html_content)
        html = html_template.render(**context)

        # Render plain text (or use simple version)
        body = email_template.text_content or f"Hello {participant.name},\n\nPlease see the attached ticket for {event.name}."

        # Prepare attachments
        attachments = []
        if attach_pdf:
            # Generate PDF ticket
            pdf_content = generate_ticket_pdf(participant_id)
            if pdf_content:
                attachments.append({
                    'filename': f"ticket_{participant.name.replace(' ', '_')}.pdf",
                    'content': pdf_content
                })

        # Prepare embedded images (for CID references in HTML)
        embedded_images = []

        # Extract CID references from HTML and fetch images
        import re
        cid_pattern = r'cid:([^"\'>\s]+)'
        cids = re.findall(cid_pattern, html)

        for cid in cids:
            # Find image by CID
            image = ImageAttachment.query.filter_by(cid=cid, is_active=True).first()
            if image:
                # Load image file
                project_root = Path(current_app.root_path).parent
                image_path = project_root / image.file_path

                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        embedded_images.append({
                            'cid': cid,
                            'filename': image.original_filename,
                            'content': f.read()
                        })

        # Send email
        success, error = send_email(
            recipient=participant.email,
            subject=subject,
            body=body,
            html=html,
            attachments=attachments if attachments else None,
            embedded_images=embedded_images if embedded_images else None
        )

        # Log the email
        email_log = EmailLog(
            event_id=event.id,
            recipient_email=participant.email,
            subject=subject,
            template_name=email_template.name,
            status='sent' if success else 'failed',
            sent_at=datetime.utcnow() if success else None,
            error_message=error
        )
        db.session.add(email_log)
        db.session.commit()

        return success, error

    except Exception as e:
        current_app.logger.error(f"Error sending ticket email: {str(e)}", exc_info=True)
        return False, str(e)


def send_bulk_ticket_emails(event_id, template_id=None, attach_pdf=True):
    """
    Send ticket emails to all participants in an event

    Args:
        event_id: Event ID
        template_id: Email template ID (optional)
        attach_pdf: Whether to attach PDF tickets (default: True)

    Returns:
        Dict with success count and errors
    """
    from app.models.events import Participant

    participants = Participant.query.filter_by(event_id=event_id).all()

    success_count = 0
    failed_count = 0
    errors = []

    for participant in participants:
        success, error = send_ticket_email(participant.id, template_id, attach_pdf)

        if success:
            success_count += 1
        else:
            failed_count += 1
            errors.append({
                'participant_id': str(participant.id),
                'email': participant.email,
                'error': error
            })

    return {
        'success': True,
        'total': len(participants),
        'success_count': success_count,
        'failed_count': failed_count,
        'errors': errors
    }

