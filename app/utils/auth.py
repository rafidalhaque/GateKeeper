"""
Authentication utilities for Supabase JWT validation
Following plan.md: JWT-based auth validation with session-based auth state
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify, g, session, redirect, url_for
from app.models.auth import AdminUser


def verify_jwt_token(token):
    """Verify Supabase JWT token"""
    try:
        secret = os.getenv('SUPABASE_JWT_SECRET')
        if not secret:
            return None
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=['HS256'],
            audience='authenticated'
        )
        
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user():
    """Get current authenticated user from session or JWT"""
    # Check session first (server-side auth state)
    if 'user_id' in session:
        return AdminUser.query.get(session['user_id'])

    # Fallback to JWT validation for API calls
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)

        if payload:
            supabase_user_id = payload.get('sub')
            user = AdminUser.query.filter_by(supabase_user_id=supabase_user_id).first()

            # Store in session for subsequent requests
            if user:
                session['user_id'] = str(user.id)
                session['supabase_user_id'] = supabase_user_id

            return user

    return None


def login_required(f):
    """API decorator: require authentication, return JSON errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """HTML decorator: require authentication, redirect to login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('frontend.login', next=request.url))

        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


def permission_required(*permissions):
    """Decorator to require specific permissions (API endpoints)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Super admin bypasses all checks
            if user.is_super_admin:
                g.current_user = user
                return f(*args, **kwargs)
            
            # Check permissions
            if not user.has_any_permission(permissions):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            g.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def super_admin_required(f):
    """Decorator to require super admin access (API endpoints)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not user.is_super_admin:
            return jsonify({'error': 'Super admin access required'}), 403
        
        g.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function
