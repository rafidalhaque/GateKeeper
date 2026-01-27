"""
Admin user invitation routes
"""
from flask import Blueprint, request, jsonify, current_app
from app.models import db
from app.models.auth import PendingInvitation, Role, AdminUser
from app.utils.auth import super_admin_required, get_current_user
from datetime import datetime, timedelta
import secrets
import uuid

bp = Blueprint('invitations', __name__, url_prefix='/api/invitations')


def create_supabase_user(email, name):
    """Create user in Supabase Auth and return user ID"""
    import requests

    supabase_url = current_app.config.get('SUPABASE_URL')
    supabase_service_key = current_app.config.get('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_service_key:
        raise Exception(
            'Supabase configuration not found. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file. '
            'See SUPABASE_SERVICE_KEY_SETUP.md for instructions.'
        )

    # Check if service key is still the placeholder
    if supabase_service_key == 'YOUR_SERVICE_ROLE_KEY_HERE':
        raise Exception(
            'SUPABASE_SERVICE_KEY is not configured. Please replace YOUR_SERVICE_ROLE_KEY_HERE with your actual '
            'service role key from Supabase dashboard. See SUPABASE_SERVICE_KEY_SETUP.md for instructions.'
        )

    # Create user in Supabase
    headers = {
        'apikey': supabase_service_key,
        'Authorization': f'Bearer {supabase_service_key}',
        'Content-Type': 'application/json'
    }

    # Generate random password (user will set their own)
    temp_password = secrets.token_urlsafe(32)

    response = requests.post(
        f'{supabase_url}/auth/v1/admin/users',
        headers=headers,
        json={
            'email': email,
            'password': temp_password,
            'email_confirm': False,  # We'll handle verification through invitation link
            'user_metadata': {
                'name': name
            }
        }
    )

    if response.status_code not in [200, 201]:
        raise Exception(f'Failed to create Supabase user: {response.text}')

    user_data = response.json()
    return user_data['id']


@bp.route('/', methods=['POST'])
@super_admin_required
def create_invitation():
    """Create admin user invitation (super admin only)"""
    data = request.get_json()
    current_user = get_current_user()

    # Validate required fields
    if 'email' not in data:
        return jsonify({'error': 'Missing email'}), 400

    email = data['email'].lower().strip()
    name = data.get('name', '')
    role_id = data.get('role_id')

    # Check if user already exists
    existing_user = AdminUser.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400

    # Check if invitation already exists
    existing_invitation = PendingInvitation.query.filter_by(
        email=email,
        status='pending'
    ).first()

    if existing_invitation:
        return jsonify({'error': 'Pending invitation already exists for this email'}), 400

    # Validate role
    if role_id:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Invalid role_id'}), 400

    try:
        # Create user in Supabase
        supabase_user_id = create_supabase_user(email, name)

        # Generate invitation token
        invitation_token = secrets.token_urlsafe(32)

        # Create invitation record
        invitation = PendingInvitation(
            email=email,
            name=name,
            role_id=role_id,
            invited_by=current_user.id,
            invitation_token=invitation_token,
            supabase_user_id=supabase_user_id,
            expires_at=datetime.utcnow() + timedelta(days=7),  # 7 days expiry
            status='pending'
        )

        db.session.add(invitation)
        db.session.commit()

        # Generate invitation link
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')
        invitation_link = f"{frontend_url}/accept-invitation?token={invitation_token}"

        return jsonify({
            'message': 'Invitation created successfully',
            'invitation': {
                'id': str(invitation.id),
                'email': invitation.email,
                'name': invitation.name,
                'role_id': invitation.role_id,
                'invitation_link': invitation_link,
                'expires_at': invitation.expires_at.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create invitation: {str(e)}'}), 500


@bp.route('/', methods=['GET'])
@super_admin_required
def list_invitations():
    """List all pending invitations (super admin only)"""
    invitations = PendingInvitation.query.filter_by(status='pending').order_by(
        PendingInvitation.created_at.desc()
    ).all()

    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5000')

    return jsonify([{
        'id': str(inv.id),
        'email': inv.email,
        'name': inv.name,
        'role_id': inv.role_id,
        'role_name': inv.role.name if inv.role else None,
        'invited_by': inv.inviter.name if inv.inviter else None,
        'invitation_link': f"{frontend_url}/accept-invitation?token={inv.invitation_token}",
        'expires_at': inv.expires_at.isoformat(),
        'status': inv.status,
        'created_at': inv.created_at.isoformat()
    } for inv in invitations])


@bp.route('/<uuid:invitation_id>', methods=['DELETE'])
@super_admin_required
def revoke_invitation(invitation_id):
    """Revoke/delete an invitation (super admin only)"""
    invitation = PendingInvitation.query.get_or_404(invitation_id)

    # Update status instead of deleting (for audit trail)
    invitation.status = 'revoked'
    db.session.commit()

    return jsonify({'message': 'Invitation revoked successfully'})


@bp.route('/verify/<token>', methods=['GET'])
def verify_invitation(token):
    """Verify invitation token (public endpoint)"""
    invitation = PendingInvitation.query.filter_by(
        invitation_token=token
    ).first()

    if not invitation:
        return jsonify({'error': 'Invalid invitation token'}), 404

    if invitation.status != 'pending':
        return jsonify({'error': f'Invitation is {invitation.status}'}), 400

    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.session.commit()
        return jsonify({'error': 'Invitation has expired'}), 400

    return jsonify({
        'valid': True,
        'email': invitation.email,
        'name': invitation.name,
        'role_name': invitation.role.name if invitation.role else None
    })


@bp.route('/accept', methods=['POST'])
def accept_invitation():
    """Accept invitation and set password (public endpoint)"""
    data = request.get_json()

    token = data.get('token')
    password = data.get('password')

    if not token or not password:
        return jsonify({'error': 'Missing token or password'}), 400

    # Validate invitation
    invitation = PendingInvitation.query.filter_by(
        invitation_token=token,
        status='pending'
    ).first()

    if not invitation:
        return jsonify({'error': 'Invalid or expired invitation'}), 404

    if invitation.expires_at < datetime.utcnow():
        invitation.status = 'expired'
        db.session.commit()
        return jsonify({'error': 'Invitation has expired'}), 400

    try:
        # Update password in Supabase
        import requests

        supabase_url = current_app.config.get('SUPABASE_URL')
        supabase_service_key = current_app.config.get('SUPABASE_SERVICE_KEY')

        if not supabase_url or not supabase_service_key or supabase_service_key == 'YOUR_SERVICE_ROLE_KEY_HERE':
            raise Exception(
                'Supabase configuration not found. Please configure SUPABASE_SERVICE_KEY. '
                'See SUPABASE_SERVICE_KEY_SETUP.md for instructions.'
            )

        headers = {
            'apikey': supabase_service_key,
            'Authorization': f'Bearer {supabase_service_key}',
            'Content-Type': 'application/json'
        }

        # Update user password and confirm email
        response = requests.put(
            f'{supabase_url}/auth/v1/admin/users/{invitation.supabase_user_id}',
            headers=headers,
            json={
                'password': password,
                'email_confirm': True  # Auto-verify email
            }
        )

        if response.status_code not in [200, 201]:
            raise Exception(f'Failed to update Supabase user: {response.text}')

        # Create AdminUser record
        admin_user = AdminUser(
            supabase_user_id=invitation.supabase_user_id,
            email=invitation.email,
            name=invitation.name,
            role_id=invitation.role_id,
            is_super_admin=False
        )

        db.session.add(admin_user)

        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.accepted_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Invitation accepted successfully',
            'email': admin_user.email
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to accept invitation: {str(e)}'}), 500
