"""
Frontend template routes
"""
from flask import Blueprint, render_template, request, current_app, make_response
import csv
import io
from app.models.events import Participant, Event
from app.utils.auth import admin_required, permission_required_html

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
    return render_template('index.html')


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


@bp.route('/admin/events/<uuid:event_id>/configure')
@admin_required
def event_configuration(event_id):
    """Event configuration page for custom fields and schedule"""
    return render_template('admin/event_config.html', event_id=str(event_id))


@bp.route('/admin/events/<uuid:event_id>/csv-template')
@admin_required
def download_csv_template(event_id):
    """Download CSV template with custom fields for an event"""
    event = Event.query.get_or_404(event_id)

    # Standard columns based on event mode (t_shirt_size is now a custom field)
    if event.mode == 'team':
        headers = ['team_id', 'team_name', 'member_name', 'member_email']
    else:  # solo
        headers = ['participant_name', 'participant_email']

    # Add custom field columns
    if event.custom_fields:
        custom_field_names = [field['name'] for field in event.custom_fields if 'name' in field]
        headers.extend(custom_field_names)

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)

    # Add example row with comments
    if event.mode == 'team':
        example_row = ['TEAM001', 'Team Alpha', 'John Doe', 'john@example.com']
    else:
        example_row = ['John Doe', 'john@example.com']

    # Add example values for custom fields
    if event.custom_fields:
        for field in event.custom_fields:
            if 'name' not in field:
                continue
            field_type = field.get('type', 'text')

            # Add example based on field type
            if field_type == 'select' and field.get('options'):
                # Use first option as example
                options = [opt.strip() for opt in field['options'].split(',')]
                example_row.append(options[0] if options else '')
            elif field_type == 'checkbox':
                example_row.append('Yes')
            elif field_type == 'email':
                example_row.append('example@email.com')
            elif field_type == 'number':
                example_row.append('123')
            else:
                example_row.append(f"Sample {field.get('label', field['name'])}")

    writer.writerow(example_row)

    # Return as download
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=event_{event.name.replace(" ", "_")}_template.csv'

    return response


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


@bp.route('/admin/ticket-designer')
@admin_required
@permission_required_html('ticket.create')
def admin_ticket_designer():
    """Ticket designer page - requires ticket.create permission"""
    return render_template('admin/ticket_designer.html', config=get_supabase_config())


@bp.route('/admin/token-designer')
@admin_required
@permission_required_html('token.create')
def admin_token_designer():
    """Token/Badge designer page - requires token.create permission"""
    return render_template('admin/token_designer.html', config=get_supabase_config())


@bp.route('/admin/css-guide')
@admin_required
def admin_css_guide():
    """CSS Guide page for designers - accessible to all admins"""
    return render_template('admin/css_guide.html', config=get_supabase_config())


@bp.route('/admin/image-library')
@admin_required
@permission_required_html('manage_email_templates')
def admin_image_library():
    """Image library page for managing template images"""
    return render_template('admin/image_library.html', config=get_supabase_config())


@bp.route('/admin/jobs')
@admin_required
def admin_jobs():
    """Background jobs monitoring page - accessible to all admins"""
    return render_template('admin/jobs.html', config=get_supabase_config())


@bp.route('/accept-invitation')
def accept_invitation():
    """Invitation acceptance page (public)"""
    token = request.args.get('token')
    return render_template('accept_invitation.html', token=token, config=get_supabase_config())

