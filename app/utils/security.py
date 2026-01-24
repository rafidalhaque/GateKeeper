"""
Security utilities and middleware
"""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib


# Rate limiting storage (in production, use Redis)
_rate_limit_storage = {}


def rate_limit(limit=10, window=60):
    """
    Rate limiting decorator
    
    Args:
        limit: Number of requests allowed in the window
        window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            
            # Create key for this endpoint and IP
            key = f"{f.__name__}:{client_ip}"
            
            now = datetime.utcnow()
            
            # Clean old entries
            if key in _rate_limit_storage:
                _rate_limit_storage[key] = [
                    timestamp for timestamp in _rate_limit_storage[key]
                    if now - timestamp < timedelta(seconds=window)
                ]
            
            # Check rate limit
            if key not in _rate_limit_storage:
                _rate_limit_storage[key] = []
            
            if len(_rate_limit_storage[key]) >= limit:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {limit} requests per {window} seconds'
                }), 429
            
            # Add current request
            _rate_limit_storage[key].append(now)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def generate_device_fingerprint(request):
    """Generate a device fingerprint from request"""
    components = [
        request.remote_addr,
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        request.headers.get('Accept-Encoding', '')
    ]
    
    fingerprint_string = '|'.join(components)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()


def validate_origin(allowed_origins):
    """
    Validate request origin
    
    Args:
        allowed_origins: List of allowed origins
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            origin = request.headers.get('Origin')
            
            if origin and origin not in allowed_origins:
                return jsonify({
                    'error': 'Invalid origin',
                    'message': 'Request from unauthorized origin'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_https(f):
    """Require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        
        if current_app.config['FLASK_ENV'] == 'production':
            if not request.is_secure:
                return jsonify({
                    'error': 'HTTPS required',
                    'message': 'This endpoint requires HTTPS'
                }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal"""
    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')
    
    # Remove parent directory references
    filename = filename.replace('..', '')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def validate_content_type(allowed_types):
    """
    Validate request content type
    
    Args:
        allowed_types: List of allowed content types
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.content_type
            
            if content_type not in allowed_types:
                return jsonify({
                    'error': 'Invalid content type',
                    'message': f'Content type must be one of: {", ".join(allowed_types)}'
                }), 415
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
