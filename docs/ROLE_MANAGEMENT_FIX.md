# Role Management Fix

## Problem

The Roles tab on `/admin/users` page had the following issues:
1. "Create Role" button had no response (modal not implemented)
2. "Edit" button had no functionality
3. No delete functionality
4. Super Admin role was not protected from editing/deletion

## Solution

### 1. Backend Changes (`app/routes/admin.py`)

#### Added GET endpoint for single role
```python
@bp.route('/roles/<int:role_id>', methods=['GET'])
@permission_required('role.read')
def get_role(role_id):
    """Get single role with permissions"""
```
This allows fetching full role details including all assigned permissions for editing.

#### Protected Super Admin role from deletion
```python
@bp.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    # Prevent deletion of Super Admin role
    if role.name == 'Super Admin':
        return jsonify({'error': 'Cannot delete Super Admin role'}), 403
```

#### Protected Super Admin role from being renamed
```python
@bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    # Prevent renaming Super Admin role
    if role.name == 'Super Admin' and 'name' in data and data['name'] != 'Super Admin':
        return jsonify({'error': 'Cannot rename Super Admin role'}), 403
```

#### Enhanced roles list endpoint
Now returns permissions array with each role for display purposes.

### 2. Frontend Changes (`app/templates/admin/users.html`)

#### Added Create/Edit Role Modal
- Form with role name, description fields
- Checkbox list of all available permissions grouped by feature
- Creates new role or updates existing role
- Disables name field when editing Super Admin role

#### Added Delete Confirmation Modal
- Shows warning if role is assigned to users
- Prevents deletion of roles with assigned users
- Super Admin role doesn't show delete button at all

#### Updated Role Cards
- Added "Protected" badge for Super Admin role
- Added "Edit" and "Delete" buttons with functionality
- Delete button hidden for Super Admin role
- Shows user count and permission count

#### Complete JavaScript Implementation
- `openCreateRoleModal()` - Opens modal for new role
- `openEditRoleModal(role)` - Loads role details and opens edit modal
- `saveRole()` - Creates or updates role via API
- `confirmDeleteRole(role)` - Shows delete confirmation
- `deleteRole()` - Deletes role after confirmation
- `loadAllPermissions()` - Fetches all permissions for checkbox list

## Features

### Role Creation
1. Click "Create Role" button
2. Fill in role name and description
3. Select permissions from grouped checkboxes
4. Click "Create"
5. Role is created and list refreshes

### Role Editing
1. Click "Edit" on any role card
2. Modal opens with current role data pre-filled
3. Modify name, description, or permissions
4. Click "Update"
5. Role is updated and list refreshes

**Note**: Super Admin role name cannot be changed (field is disabled)

### Role Deletion
1. Click "Delete" on any role card (except Super Admin)
2. Confirmation modal appears
3. If role has users, delete button is disabled with warning
4. Click "Delete" to confirm
5. Role is deleted and list refreshes

**Note**: Super Admin role has no delete button

### Protections

#### Super Admin Role
- ✅ Cannot be deleted
- ✅ Cannot be renamed
- ✅ Shows "Protected" badge
- ✅ Can still edit permissions
- ✅ Can still edit description

#### Roles with Assigned Users
- ✅ Cannot be deleted
- ✅ Shows warning with user count
- ✅ Delete button disabled in modal
- ⚠️ Must reassign users before deletion

## API Endpoints

### Get All Roles
```http
GET /api/admin/roles
Authorization: Bearer <token>
Permission: role.read

Response: [
  {
    "id": 1,
    "name": "Event Admin",
    "description": "Full event management",
    "permission_count": 15,
    "user_count": 3,
    "permissions": [
      {"id": 1, "key": "event.read", "description": "Read events"},
      ...
    ]
  }
]
```

### Get Single Role
```http
GET /api/admin/roles/<role_id>
Authorization: Bearer <token>
Permission: role.read

Response: {
  "id": 1,
  "name": "Event Admin",
  "description": "Full event management",
  "permission_count": 15,
  "user_count": 3,
  "permissions": [...],
  "created_at": "2026-01-25T00:00:00",
  "updated_at": "2026-01-25T00:00:00"
}
```

### Create Role
```http
POST /api/admin/roles
Authorization: Bearer <token>
Permission: super_admin (super_admin_required decorator)
Content-Type: application/json

{
  "name": "New Role",
  "description": "Role description",
  "permission_ids": [1, 2, 3, 4]
}

Response: {
  "id": 5,
  "name": "New Role",
  "description": "Role description",
  "created_at": "2026-01-25T12:00:00"
}
```

### Update Role
```http
PUT /api/admin/roles/<role_id>
Authorization: Bearer <token>
Permission: super_admin
Content-Type: application/json

{
  "name": "Updated Role",
  "description": "New description",
  "permission_ids": [1, 2, 3]
}

Response: {
  "id": 5,
  "name": "Updated Role",
  "updated_at": "2026-01-25T12:30:00"
}

Errors:
- 403: Cannot rename Super Admin role
```

### Delete Role
```http
DELETE /api/admin/roles/<role_id>
Authorization: Bearer <token>
Permission: super_admin

Response: {
  "message": "Role deleted successfully"
}

Errors:
- 403: Cannot delete Super Admin role
- 400: Cannot delete role with assigned users
```

## How to Test

### 1. Access the Page
Navigate to: `http://localhost:5000/admin/users`
Click on the "Roles" tab

### 2. Test Create Role
1. Click "Create Role" button
2. Enter role name: "Test Role"
3. Enter description: "Testing role creation"
4. Select some permissions (e.g., event.read, participant.read)
5. Click "Create"
6. ✅ Should see success message
7. ✅ New role appears in the list

### 3. Test Edit Role
1. Click "Edit" on "Test Role"
2. Change description
3. Add/remove some permissions
4. Click "Update"
5. ✅ Should see success message
6. ✅ Changes reflected in role card

### 4. Test Super Admin Protection
1. Try to edit "Super Admin" role
2. ✅ Name field should be disabled
3. ✅ Can still edit permissions
4. ✅ No delete button on Super Admin card
5. ✅ Shows "Protected" badge

### 5. Test Delete Role
1. Click "Delete" on "Test Role"
2. Confirmation modal appears
3. Click "Delete"
4. ✅ Role is deleted
5. ✅ Disappears from list

### 6. Test Delete Prevention
1. Create a role and assign it to a user (if possible)
2. Try to delete the role
3. ✅ Warning message shows user count
4. ✅ Delete button is disabled

## Browser Console Testing

Check for errors/success:
```javascript
// Should see on create:
"Role created successfully"

// Should see on update:
"Role updated successfully"

// Should see on delete:
"Role deleted successfully"

// Should NOT see any errors
```

## Related Files

- `app/routes/admin.py` - Role management API endpoints
- `app/templates/admin/users.html` - Frontend UI with modals
- `app/models/auth.py` - Role and Permission models
- `app/utils/auth.py` - Permission checking decorators

## Future Enhancements

- [ ] Bulk permission assignment by feature group
- [ ] Role templates/presets
- [ ] Role duplication feature
- [ ] Permission search/filter in modal
- [ ] Audit log for role changes
- [ ] Role usage analytics
