"""
Frontend template routes
"""
from flask import Blueprint, render_template
from app.models.events import Participant, Event
from app.utils.auth import login_required, permission_required

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    """Home page"""
    return render_template('base.html', show_nav=True)


@bp.route('/ticket/<uuid:unique_uuid>')
def ticket(unique_uuid):
    """Public ticket view page"""
    participant = Participant.query.filter_by(unique_url_uuid=unique_uuid).first_or_404()
    event = Event.query.get(participant.event_id)
    
    return render_template('ticket.html', participant=participant, event=event, show_nav=False)


# Admin Routes
# NOTE: Authentication is handled client-side via JWT tokens stored in localStorage.
# The Alpine.js components use authFetch() which adds the Authorization header.
# For production, consider adding server-side authentication middleware that:
# 1. Checks for tokens in cookies/session instead of requiring client-side headers
# 2. Redirects to login page instead of returning 401 JSON responses
# Example: @login_required decorator could be adapted to work with HTML routes
@bp.route('/admin')
def admin_dashboard():
    """Admin dashboard home"""
    return render_template('admin/dashboard.html')


@bp.route('/admin/scanner')
def admin_scanner():
    """QR scanner page (admin) - Requires authentication via client-side JWT"""
    return render_template('scanner.html')


@bp.route('/admin/events')
def admin_events():
    """Events management page"""
    return render_template('admin/events.html')


@bp.route('/admin/events/<uuid:event_id>')
def admin_event_detail(event_id):
    """Event detail page"""
    return render_template('admin/event_detail.html', event_id=event_id)


@bp.route('/admin/participants')
def admin_participants():
    """Participants management page"""
    return render_template('admin/participants.html')


@bp.route('/admin/teams')
def admin_teams():
    """Teams management page"""
    return render_template('admin/teams.html')


@bp.route('/admin/reports')
def admin_reports():
    """Reports and analytics page"""
    return render_template('admin/reports.html')


@bp.route('/admin/users')
def admin_users():
    """Admin users and roles page"""
    return render_template('admin/users.html')


@bp.route('/admin/settings')
def admin_settings():
    """Settings page"""
    return render_template('admin/settings.html')
