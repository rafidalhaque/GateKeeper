"""
Token/Badge generation and preview routes
"""
from flask import Blueprint, request, jsonify, send_file
from app.models.events import Event, Participant
from app.utils.auth import permission_required
from app.services.token_service import render_token_preview, generate_token_preview_pdf
import io

bp = Blueprint('tokens', __name__, url_prefix='/api/tokens')


@bp.route('/preview', methods=['POST'])
@permission_required('token.create')
def preview_token():
    """Preview token/badge HTML with custom template - requires token.create permission"""
    data = request.get_json()

    if 'event_id' not in data:
        return jsonify({'error': 'Missing event_id'}), 400

    # Get event
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    # Get participant (or use sample data)
    participant = None
    if data.get('participant_id'):
        participant = Participant.query.get(data['participant_id'])

    # If no participant, get first participant from event or use sample data
    if not participant:
        participant = Participant.query.filter_by(event_id=data['event_id']).first()

    # Generate preview HTML
    try:
        html = render_token_preview(
            event=event,
            participant=participant,
            custom_html=data.get('html_template')
        )

        return jsonify({
            'success': True,
            'html': html
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/preview-pdf', methods=['POST'])
@permission_required('token.create')
def preview_token_pdf():
    """Generate token/badge PDF preview with custom template - requires token.create permission"""
    data = request.get_json()

    if 'event_id' not in data:
        return jsonify({'error': 'Missing event_id'}), 400

    # Get event
    event = Event.query.get(data['event_id'])
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    # Get participant
    participant = None
    if data.get('participant_id'):
        participant = Participant.query.get(data['participant_id'])

    if not participant:
        participant = Participant.query.filter_by(event_id=data['event_id']).first()

    if not participant:
        return jsonify({'error': 'No participants found for this event'}), 404

    # Generate PDF
    try:
        pdf = generate_token_preview_pdf(
            event=event,
            participant=participant,
            custom_html=data.get('html_template')
        )

        if not pdf:
            return jsonify({'error': 'Failed to generate PDF'}), 500

        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='token_preview.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
