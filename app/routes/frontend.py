"""
Frontend template routes
"""
from flask import Blueprint, render_template, request, current_app
from app.models.events import Participant, Event
from app.utils.auth import admin_required

bp = Blueprint('frontend', __name__)


def get_supabase_config():
    """Helper to get Supabase configuration for templates"""
    return {
        'SUPABASE_URL': current_app.config.get('SUPABASE_URL'),
        'SUPABASE_KEY': current_app.config.get('SUPABASE_KEY')
    }


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


# Login page to accept client-side tokens
@bp.route('/login', methods=['GET'])
def login():
    """Render a login page that uses Supabase Auth with email/password."""
    next_param = request.args.get('next', '/admin')
    return render_template('login.html',
                         next=next_param,
                         config=get_supabase_config())


# Debug route for testing Supabase connection
@bp.route('/test-supabase')
def test_supabase():
    """Test page for Supabase authentication debugging"""
    return render_template('supabase_test.html', config=get_supabase_config())


# Debug route for testing logout functionality
@bp.route('/test-logout')
def test_logout():
    """Test page for logout functionality debugging"""
    return render_template('logout_test.html')


# Admin Routes
@bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard home"""
    return render_template('admin/dashboard.html', config=get_supabase_config())


@bp.route('/admin/scanner')
@admin_required
def admin_scanner():
    """QR scanner page (admin) - Requires authentication via client-side JWT"""
    return render_template('scanner.html', config=get_supabase_config())


@bp.route('/admin/events')
@admin_required
def admin_events():
    """Events management page"""
    return render_template('admin/events.html', config=get_supabase_config())


@bp.route('/admin/events/<uuid:event_id>')
@admin_required
def admin_event_detail(event_id):
    """Event detail page"""
    return render_template('admin/event_detail.html', event_id=event_id, config=get_supabase_config())


@bp.route('/admin/participants')
@admin_required
def admin_participants():
    """Participants management page"""
    return render_template('admin/participants.html', config=get_supabase_config())


@bp.route('/admin/teams')
@admin_required
def admin_teams():
    """Teams management page"""
    return render_template('admin/teams.html', config=get_supabase_config())


@bp.route('/admin/reports')
@admin_required
def admin_reports():
    """Reports and analytics page"""
    return render_template('admin/reports.html', config=get_supabase_config())


@bp.route('/admin/users')
@admin_required
def admin_users():
    """Admin users and roles page"""
    return render_template('admin/users.html', config=get_supabase_config())


@bp.route('/admin/settings')
@admin_required
def admin_settings():
    """Settings page"""
    return render_template('admin/settings.html', config=get_supabase_config())


@bp.route('/accept-invitation')
def accept_invitation():
    """Invitation acceptance page (public)"""
    token = request.args.get('token')
    return render_template('accept_invitation.html', token=token, config=get_supabase_config())

