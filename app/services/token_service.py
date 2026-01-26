"""
Token/Badge generation service using WeasyPrint
Similar to ticket service but optimized for smaller badge sizes
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


def render_token_template(event, participant):
    """Render token/badge HTML from template"""
    # Default template if none is configured
    default_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {
                size: 3.5in 2in;
                margin: 0;
            }
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }
            .token {
                width: 3.5in;
                height: 2in;
                padding: 15px;
                box-sizing: border-box;
                border: 2px solid #333;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 16px;
                font-weight: bold;
            }
            .name {
                font-size: 20px;
                font-weight: bold;
            }
            .qr-section img {
                width: 60px;
                height: 60px;
            }
        </style>
    </head>
    <body>
        <div class="token">
            <div class="header">
                <h1>{{ event_name }}</h1>
            </div>
            <div class="content">
                <div class="name">{{ participant_name }}</div>
                {% if team_name %}
                <div class="team">{{ team_name }}</div>
                {% endif %}
            </div>
            <div class="qr-section">
                <img src="{{ qr_code }}" alt="QR Code">
            </div>
        </div>
    </body>
    </html>
    """

    # Use custom template if available
    template_html = event.token_template_html or default_template

    # Prepare context
    qr_code = generate_qr_code(participant.unique_url_uuid)

    context = {
        'event_name': event.name,
        'event_date': event.date.strftime('%Y-%m-%d'),
        'venue': event.venue or 'TBA',
        'participant_name': participant.name,
        'email': participant.email,
        'participant_uuid': str(participant.unique_url_uuid),
        'qr_code': qr_code
    }

    # Add team info if applicable
    if participant.team:
        context['team_name'] = participant.team.team_name
        context['team_id'] = participant.team.id

    # Add custom fields if available
    if participant.custom_data:
        context['custom_fields'] = participant.custom_data

    # Render template
    template = Template(template_html)
    html = template.render(**context)

    return html


def generate_token_pdf(participant_id):
    """Generate token/badge PDF for a participant"""
    participant = Participant.query.get(participant_id)
    if not participant:
        return None

    event = participant.event
    html = render_token_template(event, participant)

    # Generate PDF with WeasyPrint
    try:
        pdf = HTML(string=html).write_pdf()
        return pdf
    except Exception as e:
        print(f"Error generating token PDF: {e}")
        return None


def render_token_preview(event, participant=None, custom_html=None):
    """Render token preview HTML (for designer)"""
    # Use sample data if no participant
    if not participant:
        from datetime import datetime
        class SampleParticipant:
            name = "John Doe"
            email = "john@example.com"
            unique_url_uuid = "sample-uuid-1234"
            team = None
            custom_data = {}
        participant = SampleParticipant()

    # Use custom template if provided
    template_html = custom_html or event.token_template_html

    if not template_html:
        # Default template
        template_html = """
        <div style="border: 2px solid #333; padding: 20px; text-align: center;">
            <h2>{{ event_name }}</h2>
            <p>{{ participant_name }}</p>
            <img src="{{ qr_code }}" style="max-width: 100px;">
        </div>
        """

    # Prepare context
    qr_code = generate_qr_code(participant.unique_url_uuid)

    context = {
        'event_name': event.name,
        'event_date': event.date.strftime('%Y-%m-%d'),
        'venue': event.venue or 'TBA',
        'participant_name': participant.name,
        'email': participant.email,
        'participant_uuid': str(participant.unique_url_uuid),
        'qr_code': qr_code
    }

    # Add team info if applicable
    if hasattr(participant, 'team') and participant.team:
        context['team_name'] = participant.team.team_name
        context['team_id'] = participant.team.id

    # Add custom fields if available
    if hasattr(participant, 'custom_data') and participant.custom_data:
        context['custom_fields'] = participant.custom_data

    # Render template
    try:
        template = Template(template_html)
        html = template.render(**context)
        return html
    except Exception as e:
        return f"<p style='color: red;'>Template Error: {str(e)}</p>"


def generate_token_preview_pdf(event, participant, custom_html=None):
    """Generate preview PDF with custom template"""
    html = render_token_preview(event, participant, custom_html)

    try:
        pdf = HTML(string=html).write_pdf()
        return pdf
    except Exception as e:
        print(f"Error generating preview PDF: {e}")
        return None
