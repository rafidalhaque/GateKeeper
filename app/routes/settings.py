"""
Application settings API routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.settings import AppSettings
from app.utils.auth import admin_required, super_admin_required
from app.utils.auth import get_current_user

bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@bp.route('/', methods=['GET'])
@admin_required
def get_settings():
    """Get all application settings"""
    settings = AppSettings.get_all()

    # Return settings with metadata
    settings_list = []
    for setting in AppSettings.query.all():
        settings_list.append({
            'key': setting.key,
            'value': setting.value,
            'description': setting.description,
            'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
        })

    return jsonify(settings_list)


@bp.route('/<key>', methods=['GET'])
@admin_required
def get_setting(key):
    """Get a specific setting"""
    setting = AppSettings.query.filter_by(key=key).first_or_404()

    return jsonify({
        'key': setting.key,
        'value': setting.value,
        'description': setting.description,
        'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
    })


@bp.route('/', methods=['POST'])
@super_admin_required
def create_setting():
    """Create a new setting (Super Admin only)"""
    data = request.get_json()

    if 'key' not in data or 'value' not in data:
        return jsonify({'error': 'Missing required fields: key, value'}), 400

    # Check if setting already exists
    if AppSettings.query.filter_by(key=data['key']).first():
        return jsonify({'error': 'Setting already exists'}), 409

    current_user = get_current_user()

    setting = AppSettings(
        key=data['key'],
        value=str(data['value']),
        description=data.get('description'),
        updated_by=current_user.id if current_user else None
    )

    db.session.add(setting)
    db.session.commit()

    return jsonify({
        'message': 'Setting created successfully',
        'key': setting.key,
        'value': setting.value
    }), 201


@bp.route('/<key>', methods=['PUT'])
@super_admin_required
def update_setting(key):
    """Update a setting (Super Admin only)"""
    data = request.get_json()

    if 'value' not in data:
        return jsonify({'error': 'Missing required field: value'}), 400

    current_user = get_current_user()

    setting = AppSettings.set(
        key=key,
        value=data['value'],
        description=data.get('description'),
        updated_by=current_user.id if current_user else None
    )

    return jsonify({
        'message': 'Setting updated successfully',
        'key': setting.key,
        'value': setting.value
    })


@bp.route('/<key>', methods=['DELETE'])
@super_admin_required
def delete_setting(key):
    """Delete a setting (Super Admin only)"""
    setting = AppSettings.query.filter_by(key=key).first_or_404()

    db.session.delete(setting)
    db.session.commit()

    return jsonify({'message': 'Setting deleted successfully'})


@bp.route('/token-printing', methods=['GET'])
@admin_required
def get_token_printing_status():
    """Get token printing enabled status"""
    enabled = AppSettings.get('token_printing_enabled', 'true')

    # Convert to boolean
    if isinstance(enabled, str):
        enabled = enabled.lower() == 'true'

    return jsonify({
        'enabled': enabled
    })


@bp.route('/token-printing', methods=['PUT'])
@super_admin_required
def update_token_printing():
    """Update token printing setting (Super Admin only)"""
    data = request.get_json()

    if 'enabled' not in data:
        return jsonify({'error': 'Missing required field: enabled'}), 400

    current_user = get_current_user()

    setting = AppSettings.set(
        key='token_printing_enabled',
        value='true' if data['enabled'] else 'false',
        description='Enable or disable automatic token printing after check-in',
        updated_by=current_user.id if current_user else None
    )

    return jsonify({
        'message': 'Token printing setting updated successfully',
        'enabled': data['enabled']
    })


@bp.route('/theme', methods=['GET'])
@admin_required
def get_theme_preference():
    """Get current user's theme preference"""
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Get user-specific theme preference
    theme_key = f'user_theme_{current_user.id}'
    theme = AppSettings.get(theme_key, 'light')
    
    return jsonify({
        'theme': theme
    })


@bp.route('/theme', methods=['PUT'])
@admin_required
def update_theme_preference():
    """Update current user's theme preference"""
    data = request.get_json()
    
    if 'theme' not in data:
        return jsonify({'error': 'Missing required field: theme'}), 400
    
    theme = data['theme']
    if theme not in ['light', 'dark']:
        return jsonify({'error': 'Theme must be either "light" or "dark"'}), 400
    
    current_user = get_current_user()
    
    if not current_user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Store user-specific theme preference
    theme_key = f'user_theme_{current_user.id}'
    setting = AppSettings.set(
        key=theme_key,
        value=theme,
        description=f'Theme preference for user {current_user.email}',
        updated_by=current_user.id
    )
    
    return jsonify({
        'message': 'Theme preference updated successfully',
        'theme': theme
    })
