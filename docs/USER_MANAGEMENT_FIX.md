# User Management Fix

## Problem

The Users tab on `/admin/users` page had the following issues:
1. "Add User" button had no response (no modal or functionality)
2. "Edit Role" button had no functionality
3. No way to update user's role assignment
4. No way to manage super_admin status

## Solution

### 1. Backend Changes (`app/routes/admin.py`)

#### Enhanced User Role Assignment Endpoint
Updated the `/api/admin/users/<user_id>/assign-role` endpoint to handle both role assignment and super_admin status:

```python
@bp.route('/users/<uuid:user_id>/assign-role', methods=['POST'])
@super_admin_required
def assign_role(user_id):
    """Assign role to admin user and update super_admin status"""
    # Handles:
    # - Role assignment (role_id)
    # - Super admin status (is_super_admin)
```

**Request Body:**
```json
{
  "role_id": 1,
  "is_super_admin": false
}
```

### 2. Frontend Changes (`app/templates/admin/users.html`)

#### Added "Add User" Modal
- Shows informational modal explaining the user creation process
- Explains that users must be created via CLI command
- Provides the exact CLI command to use
- Informs about Supabase authentication integration

**Why CLI-based?**
This system uses Supabase for authentication. Admin users must:
1. Be created in the database via CLI
2. Have corresponding Supabase account
3. Link accounts on first login

#### Added "Edit Role" Modal
- Select role from dropdown
- Toggle super_admin checkbox
- Shows user's current information
- Updates via API on submit

#### Updated Users Table
- Added click handlers to "Edit Role" buttons
- Shows empty state when no users exist
- Displays all user information including current role

#### Complete JavaScript Implementation
- `openAddUserModal()` - Opens informational modal about user creation
- `openEditRoleModal(user)` - Opens modal to edit user's role and super_admin status
- `closeEditUserModal()` - Closes edit modal and resets form
- `saveUserRole()` - Submits role assignment via API

## Features

### Add User (Informational)
1. Click "Add User" button
2. Modal appears with instructions
3. Shows CLI command to create users
4. Explains authentication flow

**CLI Command:**
```bash
flask --app run.py create-admin --email user@example.com --name "User Name"
```

### Edit User Role
1. Click "Edit Role" on any user row
2. Modal opens with user information
3. Select new role from dropdown
4. Toggle "Super Admin" checkbox if needed
5. Click "Update"
6. User's role and super_admin status are updated

**Features:**
- ✅ Select from all available roles
- ✅ Toggle super_admin status
- ✅ See current user information
- ✅ Real-time updates after save

### Super Admin Status
The super_admin flag provides:
- Full system access regardless of role
- Can bypass permission checks
- Can manage all aspects of the system
- ⚠️ Should be used sparingly

## User Creation Flow

### 1. Create via CLI
```bash
flask --app run.py create-admin --email ahmadmusa@tuta.io --name "Ahmad Musa"
```

This creates:
- Database record in `admin_users` table
- Default role: "Event Admin"
- `is_super_admin`: False by default
- `supabase_user_id`: NULL (linked on first login)

### 2. User Creates Supabase Account
User goes to `/login` and creates account with the same email

### 3. First Login
- User logs in with Supabase credentials
- System links Supabase user_id to admin_user record
- User gains access based on assigned role

### 4. Role Management
Super admins can now:
- Assign different roles to users
- Grant/revoke super_admin status
- Manage permissions via roles

## API Endpoints

### List Admin Users
```http
GET /api/admin/users
Authorization: Bearer <token>
Permission: super_admin

Response: [
  {
    "id": "uuid...",
    "email": "user@example.com",
    "name": "User Name",
    "is_super_admin": false,
    "role_id": 1,
    "role_name": "Event Admin",
    "created_at": "2026-01-25T00:00:00"
  }
]
```

### Assign Role to User
```http
POST /api/admin/users/<user_id>/assign-role
Authorization: Bearer <token>
Permission: super_admin
Content-Type: application/json

{
  "role_id": 2,
  "is_super_admin": true
}

Response: {
  "user_id": "uuid...",
  "role_id": 2,
  "role_name": "Booth Manager",
  "is_super_admin": true
}
```

## How to Test

### 1. Access the Page
Navigate to: `http://localhost:5000/admin/users`
Users tab should be active by default

### 2. Test Add User (Informational)
1. Click "Add User" button
2. ✅ Modal appears with CLI instructions
3. ✅ Shows exact command to create users
4. ✅ Explains Supabase authentication flow
5. Click "Close"

### 3. Create a Test User via CLI
```bash
flask --app run.py create-admin --email test@example.com --name "Test User"
```
✅ User appears in the users list

### 4. Test Edit User Role
1. Click "Edit Role" on any user
2. Modal opens showing user info
3. Change role from dropdown (e.g., Event Admin → Booth Manager)
4. Toggle "Super Admin" checkbox
5. Click "Update"
6. ✅ Should see success message
7. ✅ User's role updated in table

### 5. Test Super Admin Toggle
1. Edit a user
2. Check "Super Admin" checkbox
3. Click "Update"
4. ✅ User shows "Yes" in Super Admin column
5. Edit again and uncheck
6. ✅ User shows "No" in Super Admin column

### 6. Verify Role Changes
1. Login as the modified user (if possible)
2. ✅ User should have permissions from new role
3. ✅ Super admin should have full access

## Browser Console Testing

Check for proper logging:
```javascript
// On page load:
"Users loaded: [...]"
"Roles loaded: [...]"

// On opening edit modal:
"Opening edit role modal for user: {...}"

// On saving:
"Saving user role: {role_id: 2, is_super_admin: true}"
"User role updated successfully"
```

## Important Notes

### Why Not Database User Creation?
Users are created via CLI because:
1. **Supabase Integration**: Users must have Supabase accounts for authentication
2. **Security**: Admin creation should be deliberate and logged
3. **Email Verification**: Supabase handles email verification flow
4. **Password Management**: Passwords stored securely in Supabase, not in app database

### User Linking Process
1. User created in database (via CLI)
2. User signs up in Supabase (same email)
3. On first login, system links `supabase_user_id`
4. Subsequent logins use this link for authentication

### Permission System
- **Role-based**: Users inherit permissions from assigned role
- **Super Admin Override**: Super admins bypass permission checks
- **Flexible**: Roles can be changed without recreating users

## Related Files

- `app/routes/admin.py` - User and role management API
- `app/templates/admin/users.html` - Frontend UI
- `app/models/auth.py` - AdminUser, Role models
- `app/cli.py` - create-admin CLI command
- `app/utils/auth.py` - Authentication decorators

## Future Enhancements

- [ ] Web-based user creation (with Supabase API integration)
- [ ] User deletion/deactivation
- [ ] User password reset
- [ ] Activity log for user management actions
- [ ] Bulk role assignment
- [ ] User search and filtering
- [ ] Export user list to CSV
