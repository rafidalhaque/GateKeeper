"""
PDF ticket generation service using WeasyPrint
"""
from weasyprint import HTML, CSS
from jinja2 import Template
import qrcode
import io
import base64
from app.models import db
from app.models.events import Event, Participant


def generate_qr_code(participant_uuid):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(participant_uuid)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def render_ticket_template(event, participant):
    """Render ticket HTML from template"""
    # Default template if none is configured
    default_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .ticket { border: 2px solid #333; padding: 20px; max-width: 600px; }
            .qr-code { text-align: center; margin: 20px 0; }
            .qr-code img { max-width: 200px; }
        </style>
        {{ custom_css }}
    </head>
    <body>
        <div class="ticket">
            <h1>{{ event_name }}</h1>
            <p><strong>Date:</strong> {{ event_date }}</p>
            <p><strong>Venue:</strong> {{ venue }}</p>
            <hr>
            <p><strong>Participant:</strong> {{ participant_name }}</p>
            <p><strong>Email:</strong> {{ email }}</p>
            {% if team_name %}
            <p><strong>Team:</strong> {{ team_name }} ({{ team_id }})</p>
            {% endif %}
            {% if t_shirt_size %}
            <p><strong>T-Shirt Size:</strong> {{ t_shirt_size }}</p>
            {% endif %}
            <div class="qr-code">
                <img src="{{ qr_code }}" alt="QR Code">
                <p><small>{{ participant_uuid }}</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Use custom template if available
    template_html = event.ticket_template_html or default_template
    
    # Prepare context
    from flask import current_app
    qr_code = generate_qr_code(participant.unique_url_uuid)
    
    context = {
        'event_name': event.name,
        'event_date': event.date.strftime('%Y-%m-%d'),
        'venue': event.venue or 'TBA',
        'participant_name': participant.name,
        'email': participant.email,
        'participant_uuid': str(participant.unique_url_uuid),
        't_shirt_size': participant.custom_data.get('t-shirt_size') if participant.custom_data else None,
        'qr_code': qr_code,
        'custom_css': f'<style>{event.ticket_template_css}</style>' if event.ticket_template_css else ''
    }
    
    # Add team info if applicable
    if participant.team:
        context['team_name'] = participant.team.team_name
        context['team_id'] = participant.team.id
    
    # Add custom fields if available
    if participant.custom_data:
        context['custom_fields'] = participant.custom_data
    
    # Add schedule if available
    if event.schedule_config:
        context['schedule'] = event.schedule_config
    
    # Render template
    template = Template(template_html)
    return template.render(**context)


def generate_ticket_pdf(participant_id):
    """Generate PDF ticket for a participant"""
    participant = Participant.query.get(participant_id)
    if not participant:
        return None
    
    event = Event.query.get(participant.event_id)
    if not event:
        return None
    
    # Render HTML
    html_content = render_ticket_template(event, participant)
    
    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()
    
    return pdf


def generate_bulk_tickets(event_id):
    """Generate tickets for all participants in an event"""
    participants = Participant.query.filter_by(event_id=event_id).all()
    
    generated_count = 0
    errors = []
    
    for participant in participants:
        try:
            pdf = generate_ticket_pdf(participant.id)
            if pdf:
                # TODO: Save PDF to storage or attach to email
                generated_count += 1
        except Exception as e:
            errors.append({
                'participant_id': str(participant.id),
                'error': str(e)
            })
    
    return {
        'success': True,
        'generated_count': generated_count,
        'errors': errors
    }


def render_ticket_preview(event, participant=None, custom_html=None, custom_css=None):
    """Render ticket HTML for preview with custom templates"""
    # Use sample participant data if none provided
    if not participant:
        from flask import current_app
        participant = type('Participant', (), {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'unique_url_uuid': '00000000-0000-0000-0000-000000000000',
            't_shirt_size': 'L',
            'custom_data': None,
            'team': None
        })()

    # Default template if none provided
    default_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .ticket { border: 2px solid #333; padding: 20px; max-width: 600px; }
            .qr-code { text-align: center; margin: 20px 0; }
            .qr-code img { max-width: 200px; }
        </style>
        {{ custom_css }}
    </head>
    <body>
        <div class="ticket">
            <h1>{{ event_name }}</h1>
            <p><strong>Date:</strong> {{ event_date }}</p>
            <p><strong>Venue:</strong> {{ venue }}</p>
            <hr>
            <p><strong>Participant:</strong> {{ participant_name }}</p>
            <p><strong>Email:</strong> {{ email }}</p>
            {% if team_name %}
            <p><strong>Team:</strong> {{ team_name }} ({{ team_id }})</p>
            {% endif %}
            {% if t_shirt_size %}
            <p><strong>T-Shirt Size:</strong> {{ t_shirt_size }}</p>
            {% endif %}
            <div class="qr-code">
                <img src="{{ qr_code }}" alt="QR Code">
                <p><small>{{ participant_uuid }}</small></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Use custom template if provided
    template_html = custom_html or event.ticket_template_html or default_template

    # Generate QR code
    qr_code = generate_qr_code(participant.unique_url_uuid)

    # Prepare context
    context = {
        'event_name': event.name,
        'event_date': event.date.strftime('%Y-%m-%d') if hasattr(event.date, 'strftime') else str(event.date),
        'venue': event.venue or 'TBA',
        'participant_name': participant.name,
        'email': participant.email,
        'participant_uuid': str(participant.unique_url_uuid),
        't_shirt_size': participant.custom_data.get('t_shirt_size') if hasattr(participant, 'custom_data') and participant.custom_data else getattr(participant, 't_shirt_size', None),
        'qr_code': qr_code,
        'custom_css': f'<style>{custom_css or event.ticket_template_css or ""}</style>'
    }

    # Add team info if applicable
    if hasattr(participant, 'team') and participant.team:
        context['team_name'] = participant.team.team_name
        context['team_id'] = participant.team.id

    # Add custom fields if available
    if hasattr(participant, 'custom_data') and participant.custom_data:
        context['custom_fields'] = participant.custom_data

    # Add schedule if available
    if event.schedule_config:
        context['schedule'] = event.schedule_config

    # Render template
    template = Template(template_html)
    return template.render(**context)


def generate_ticket_preview_pdf(event, participant=None, custom_html=None, custom_css=None):
    """Generate preview PDF with custom templates"""
    html_content = render_ticket_preview(event, participant, custom_html, custom_css)

    try:
        pdf = HTML(string=html_content).write_pdf()
        return pdf
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")

