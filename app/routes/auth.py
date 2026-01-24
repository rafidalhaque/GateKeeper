"""
Authentication routes for Supabase integration
Following plan.md: JWT-based validation with session-based auth state
"""
from flask import Blueprint, request, jsonify, session
from app.models.auth import AdminUser
from app.models import db
import os
import jwt

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with Supabase JWT and establish session"""
    data = request.get_json()

    if not data or 'access_token' not in data:
        return jsonify({'error': 'Missing access_token'}), 400

    access_token = data.get('access_token')

    # Verify JWT token
    secret = os.getenv('SUPABASE_JWT_SECRET')
    if not secret:
        return jsonify({'error': 'JWT secret not configured'}), 500

    try:
        payload = jwt.decode(
            access_token,
            secret,
            algorithms=['HS256'],
            audience='authenticated'
        )

        supabase_user_id = payload.get('sub')
        email = payload.get('email')
        name = payload.get('user_metadata', {}).get('name', email)

        # Find or link admin user
        admin_user = AdminUser.query.filter_by(supabase_user_id=supabase_user_id).first()

        if not admin_user:
            # Try to find by email and link
            admin_user = AdminUser.query.filter_by(email=email).first()
            if admin_user:
                admin_user.supabase_user_id = supabase_user_id
                if name:
                    admin_user.name = name
                db.session.commit()
            else:
                return jsonify({
                    'error': 'User not authorized as admin',
                    'message': 'Contact your administrator to grant admin access'
                }), 403
        else:
            # Update user info
            if email:
                admin_user.email = email
            if name:
                admin_user.name = name
            db.session.commit()

        # Establish session
        session['user_id'] = str(admin_user.id)
        session['supabase_user_id'] = supabase_user_id
        session.permanent = True

        return jsonify({
            'success': True,
            'user': {
                'id': str(admin_user.id),
                'email': admin_user.email,
                'name': admin_user.name,
                'is_super_admin': admin_user.is_super_admin
            }
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return jsonify({'error': 'Invalid or expired token'}), 401


@bp.route('/logout', methods=['POST'])
def logout():
    """Clear session and logout"""
    print(f"Logout endpoint called. Session before clear: {dict(session)}")
    session.clear()
    print(f"Session after clear: {dict(session)}")
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@bp.route('/me', methods=['GET'])
def me():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200

    admin_user = AdminUser.query.get(session['user_id'])
    if not admin_user:
        session.clear()
        return jsonify({'authenticated': False}), 200

    return jsonify({
        'authenticated': True,
        'user': {
            'id': str(admin_user.id),
            'email': admin_user.email,
            'name': admin_user.name,
            'is_super_admin': admin_user.is_super_admin
        }
    }), 200
