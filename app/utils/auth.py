"""
Authentication utilities and decorators for Supabase JWT validation
"""
import jwt
import os
from functools import wraps
from flask import request, jsonify, g
from app.models.auth import AdminUser


def verify_jwt_token(token):
    """Verify Supabase JWT token"""
    try:
        secret = os.getenv('SUPABASE_JWT_SECRET')
        if not secret:
            return None
        
        # Decode JWT token
        payload = jwt.decode(
            token,
            secret,
            algorithms=['HS256'],
            audience='authenticated'
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """Get current authenticated user from token"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = verify_jwt_token(token)
    
    if not payload:
        return None
    
    # Get user from database
    supabase_user_id = payload.get('sub')
    user = AdminUser.query.filter_by(supabase_user_id=supabase_user_id).first()
    
    return user


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Store user in g for access in route functions
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def permission_required(*permissions):
    """Decorator to require specific permissions"""
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
            
            # Check if user has any of the required permissions
            if not user.has_any_permission(permissions):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            g.current_user = user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def super_admin_required(f):
    """Decorator to require super admin access"""
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
