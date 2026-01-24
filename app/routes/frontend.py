"""
Frontend template routes
"""
from flask import Blueprint, render_template
from app.models.events import Participant, Event

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    """Home page"""
    return render_template('base.html', show_nav=True)


@bp.route('/scanner')
def scanner():
    """QR scanner page"""
    return render_template('scanner.html', show_nav=True)


@bp.route('/ticket/<uuid:unique_uuid>')
def ticket(unique_uuid):
    """Public ticket view page"""
    participant = Participant.query.filter_by(unique_url_uuid=unique_uuid).first_or_404()
    event = Event.query.get(participant.event_id)
    
    return render_template('ticket.html', participant=participant, event=event, show_nav=False)
