"""
Admin and RBAC management routes
"""
from flask import Blueprint, request, jsonify
from app.models import db
from app.models.auth import Role, Permission, AdminUser
from app.utils.auth import super_admin_required, permission_required

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# Permissions endpoints
@bp.route('/permissions', methods=['GET'])
@permission_required('permission.read')
def list_permissions():
    """List all system permissions (read-only)"""
    permissions = Permission.query.order_by(Permission.feature_group, Permission.key).all()
    
    # Group by feature
    grouped = {}
    for perm in permissions:
        if perm.feature_group not in grouped:
            grouped[perm.feature_group] = []
        grouped[perm.feature_group].append({
            'id': perm.id,
            'key': perm.key,
            'description': perm.description,
            'system_reserved': perm.system_reserved
        })
    
    return jsonify(grouped)


# Role endpoints
@bp.route('/roles', methods=['POST'])
@super_admin_required
def create_role():
    """Create a new role"""
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400
    
    # Check if role already exists
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Role already exists'}), 400
    
    role = Role(
        name=data['name'],
        description=data.get('description')
    )
    
    # Assign permissions
    if 'permission_ids' in data:
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
        role.permissions = permissions
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify({
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'created_at': role.created_at.isoformat()
    }), 201


@bp.route('/roles', methods=['GET'])
@permission_required('role.read')
def list_roles():
    """List all roles"""
    roles = Role.query.all()
    
    return jsonify([{
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permission_count': len(role.permissions),
        'user_count': len(role.admin_users)
    } for role in roles])


@bp.route('/roles/<int:role_id>', methods=['PUT'])
@super_admin_required
def update_role(role_id):
    """Update role permissions"""
    role = Role.query.get_or_404(role_id)
    data = request.get_json()
    
    if 'name' in data:
        role.name = data['name']
    if 'description' in data:
        role.description = data['description']
    if 'permission_ids' in data:
        permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
        role.permissions = permissions
    
    db.session.commit()
    
    return jsonify({
        'id': role.id,
        'name': role.name,
        'updated_at': role.updated_at.isoformat()
    })


@bp.route('/roles/<int:role_id>', methods=['DELETE'])
@super_admin_required
def delete_role(role_id):
    """Delete a role"""
    role = Role.query.get_or_404(role_id)
    
    # Check if role is in use
    if len(role.admin_users) > 0:
        return jsonify({'error': 'Cannot delete role with assigned users'}), 400
    
    db.session.delete(role)
    db.session.commit()
    
    return jsonify({'message': 'Role deleted successfully'}), 200


# Admin user endpoints
@bp.route('/users', methods=['GET'])
@super_admin_required
def list_admin_users():
    """List all admin users"""
    users = AdminUser.query.all()
    
    return jsonify([{
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'is_super_admin': user.is_super_admin,
        'role_id': user.role_id,
        'role_name': user.role.name if user.role else None,
        'created_at': user.created_at.isoformat()
    } for user in users])


@bp.route('/users/<uuid:user_id>/assign-role', methods=['POST'])
@super_admin_required
def assign_role(user_id):
    """Assign role to admin user"""
    user = AdminUser.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role_id' not in data:
        return jsonify({'error': 'Missing role_id'}), 400
    
    role = Role.query.get(data['role_id'])
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    user.role_id = role.id
    db.session.commit()
    
    return jsonify({
        'user_id': str(user.id),
        'role_id': role.id,
        'role_name': role.name
    })
