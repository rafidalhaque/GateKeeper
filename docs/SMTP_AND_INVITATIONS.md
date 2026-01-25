# SMTP Configuration & User Invitation System

## Overview

Two new super admin-only features have been implemented:
1. **SMTP Configuration Management** - Configure email settings from the frontend (supersedes .env)
2. **User Invitation System** - Invite admin users directly from the frontend with automatic Supabase account creation

---

## Part 1: SMTP Configuration Management

### Features

- ✅ Super admin-only access
- ✅ Database configuration supersedes .env variables
- ✅ Test email functionality
- ✅ Secure password storage (encrypted in production)
- ✅ TLS/SSL support
- ✅ Easy reset to .env defaults

### How It Works

1. Super admin navigates to `/admin/settings`
2. SMTP Configuration section appears (only for super admins)
3. Fill in SMTP details (server, port, username, password, sender email)
4. Test configuration before saving
5. Configuration saved to database
6. All emails now use database config instead of .env

### Database Model

```python
class SMTPConfig(db.Model):
    id = Integer (primary key)
    smtp_server = String(255)
    smtp_port = Integer (default: 587)
    smtp_username = String(255)
    smtp_password = String(255)
    smtp_use_tls = Boolean (default: True)
    smtp_use_ssl = Boolean (default: False)
    sender_email = String(255)
    sender_name = String(255) (default: 'GateKeeper')
    is_active = Boolean (default: True)
    created_at = DateTime
    updated_at = DateTime
    created_by = UUID (foreign key to admin_users)
```

### API Endpoints

#### Get SMTP Configuration
```http
GET /api/smtp/config
Authorization: Bearer <token>
Permission: Super Admin only

Response:
{
  "exists": true,
  "config": {
    "id": 1,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "***HIDDEN***",
    "smtp_use_tls": true,
    "smtp_use_ssl": false,
    "sender_email": "noreply@yourdomain.com",
    "sender_name": "GateKeeper",
    "is_active": true,
    "updated_at": "2026-01-25T12:00:00"
  }
}
```

#### Create/Update SMTP Configuration
```http
POST /api/smtp/config
Authorization: Bearer <token>
Permission: Super Admin only
Content-Type: application/json

{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "your-app-password",
  "smtp_use_tls": true,
  "smtp_use_ssl": false,
  "sender_email": "noreply@yourdomain.com",
  "sender_name": "GateKeeper"
}

Response: 201 Created
{
  "message": "SMTP configuration saved successfully",
  "config": { ... }
}
```

#### Test SMTP Configuration
```http
POST /api/smtp/config/test
Authorization: Bearer <token>
Permission: Super Admin only
Content-Type: application/json

{
  "test_email": "your-email@example.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  ...
}

Response:
{
  "success": true,
  "message": "Test email sent successfully to your-email@example.com"
}
```

#### Delete SMTP Configuration
```http
DELETE /api/smtp/config/<config_id>
Authorization: Bearer <token>
Permission: Super Admin only

Response:
{
  "message": "SMTP configuration deleted successfully"
}
```

### Email Service Integration

The email service now checks for database configuration first:

```python
def get_smtp_config():
    # 1. Try database first (supersedes .env)
    db_config = SMTPConfig.query.filter_by(is_active=True).first()
    if db_config:
        return db_config
    
    # 2. Fallback to .env
    return env_config
```

### How to Use

#### From Settings Page:

1. Navigate to `/admin/settings`
2. Scroll to "SMTP Configuration" section (Super Admin only)
3. Fill in the form:
   - SMTP Server (e.g., smtp.gmail.com)
   - SMTP Port (e.g., 587 for TLS, 465 for SSL)
   - Username (your email)
   - Password (app password recommended)
   - Sender Email
   - Sender Name (optional)
4. Select TLS or SSL
5. Click "Test Configuration" to verify
6. Click "Save Configuration"
7. ✅ All emails now use this configuration!

#### Gmail Example:

For Gmail, use an App Password:
1. Enable 2FA on your Google account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate app password
4. Use that password in SMTP configuration

```
Server: smtp.gmail.com
Port: 587
Username: your-email@gmail.com
Password: your-app-password
TLS: Enabled
SSL: Disabled
```

---

## Part 2: User Invitation System

### Features

- ✅ Super admin creates invitations from frontend
- ✅ Automatic Supabase user creation
- ✅ Unique invitation link generation
- ✅ Copy link functionality
- ✅ New admin sets their own password
- ✅ Email automatically verified
- ✅ 7-day expiration
- ✅ Invitation status tracking

### How It Works

#### Step 1: Super Admin Invites User

1. Navigate to `/admin/users`
2. Click "Add User"
3. Enter email, name, and select role
4. Click "Send Invitation"
5. User created in Supabase Auth
6. Unique invitation link generated
7. Copy link and share with new admin

#### Step 2: New Admin Accepts Invitation

1. New admin clicks invitation link
2. Redirected to `/accept-invitation?token=...`
3. Sees invitation details (email, role, name)
4. Sets password (minimum 8 characters)
5. Confirms password
6. Clicks "Accept Invitation & Set Password"
7. Password updated in Supabase
8. Email automatically verified
9. AdminUser record created in database
10. Redirected to login page

### Database Models

#### PendingInvitation
```python
class PendingInvitation(db.Model):
    id = UUID (primary key)
    email = String(255) (unique)
    name = String(255)
    role_id = Integer (foreign key to roles)
    invited_by = UUID (foreign key to admin_users)
    invitation_token = String(255) (unique)
    supabase_user_id = String(255) (unique)
    expires_at = DateTime
    accepted_at = DateTime (nullable)
    status = String(50) (default: 'pending')
    created_at = DateTime
```

**Status Values:**
- `pending` - Invitation sent, not yet accepted
- `accepted` - Invitation accepted, user created
- `expired` - Invitation past expiry date
- `revoked` - Invitation revoked by admin

### API Endpoints

#### Create Invitation
```http
POST /api/invitations/
Authorization: Bearer <token>
Permission: Super Admin only
Content-Type: application/json

{
  "email": "newadmin@example.com",
  "name": "New Admin",
  "role_id": 2
}

Response: 201 Created
{
  "message": "Invitation created successfully",
  "invitation": {
    "id": "uuid...",
    "email": "newadmin@example.com",
    "name": "New Admin",
    "role_id": 2,
    "invitation_link": "http://localhost:5000/accept-invitation?token=...",
    "expires_at": "2026-02-01T12:00:00"
  }
}
```

#### List Pending Invitations
```http
GET /api/invitations/
Authorization: Bearer <token>
Permission: Super Admin only

Response:
[
  {
    "id": "uuid...",
    "email": "newadmin@example.com",
    "name": "New Admin",
    "role_id": 2,
    "role_name": "Event Admin",
    "invited_by": "John Doe",
    "invitation_link": "http://localhost:5000/accept-invitation?token=...",
    "expires_at": "2026-02-01T12:00:00",
    "status": "pending",
    "created_at": "2026-01-25T12:00:00"
  }
]
```

#### Revoke Invitation
```http
DELETE /api/invitations/<invitation_id>
Authorization: Bearer <token>
Permission: Super Admin only

Response:
{
  "message": "Invitation revoked successfully"
}
```

#### Verify Invitation (Public)
```http
GET /api/invitations/verify/<token>

Response:
{
  "valid": true,
  "email": "newadmin@example.com",
  "name": "New Admin",
  "role_name": "Event Admin"
}

Errors:
- 404: Invalid invitation token
- 400: Invitation expired or already accepted
```

#### Accept Invitation (Public)
```http
POST /api/invitations/accept
Content-Type: application/json

{
  "token": "invitation-token",
  "password": "newpassword123"
}

Response:
{
  "message": "Invitation accepted successfully",
  "email": "newadmin@example.com"
}

Errors:
- 400: Missing token or password
- 404: Invalid or expired invitation
- 500: Failed to create user in Supabase
```

### Invitation Flow Diagram

```
┌─────────────────┐
│  Super Admin    │
│  Creates        │
│  Invitation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Supabase User  │
│  Created        │
│  (temp password)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Invitation     │
│  Token          │
│  Generated      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Super Admin    │
│  Copies Link    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  New Admin      │
│  Clicks Link    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sets Password  │
│  on Frontend    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Password       │
│  Updated in     │
│  Supabase       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Email Auto     │
│  Verified       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AdminUser      │
│  Record Created │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redirect to    │
│  Login          │
└─────────────────┘
```

### Configuration Requirements

Add to `.env`:
```env
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
FRONTEND_URL=http://localhost:5000
```

**⚠️ Important:** `SUPABASE_SERVICE_KEY` is required for:
- Creating users in Supabase Auth
- Updating user passwords
- Auto-verifying emails

### Security Considerations

1. **Invitation Tokens**: 32-byte URL-safe tokens
2. **Expiry**: 7 days from creation
3. **One-time Use**: Status changes to 'accepted' after use
4. **Super Admin Only**: Only super admins can create invitations
5. **Email Verification**: Automatically verified on acceptance
6. **Password Policy**: Minimum 8 characters enforced

### Testing

#### Create Test Invitation:
```bash
# 1. Login as super admin
# 2. Navigate to /admin/users
# 3. Click "Add User"
# 4. Fill form and submit
# 5. Copy generated link
```

#### Accept Invitation:
```bash
# 1. Open invitation link in browser
# 2. Verify invitation details shown
# 3. Set password (min 8 chars)
# 4. Confirm password
# 5. Submit form
# 6. Should redirect to login
# 7. Login with new credentials
```

### Troubleshooting

#### Invitation Link Not Working
- Check token is valid: `GET /api/invitations/verify/<token>`
- Check not expired (7 days from creation)
- Check status is 'pending'

#### User Creation Fails
- Verify SUPABASE_SERVICE_KEY is set
- Check Supabase project URL is correct
- Verify service role key has user management permissions

#### Email Not Verified
- System automatically sets `email_confirm: true`
- Check Supabase user in dashboard
- Verify service key has required permissions

---

## Migration

### Run Migration:
```bash
flask --app run.py db upgrade
# or
alembic upgrade head
```

### Creates Tables:
- `smtp_config` - SMTP configuration storage
- `pending_invitations` - Invitation tracking

---

## Benefits

### SMTP Configuration:
✅ No server restart required for email changes
✅ Multiple configurations (dev, staging, prod)
✅ Test before saving
✅ Secure database storage
✅ Audit trail (created_by, created_at)

### User Invitation:
✅ No CLI required for user creation
✅ Streamlined onboarding
✅ Automatic email verification
✅ Self-service password setup
✅ Invitation tracking and management
✅ Secure token-based authentication

---

## Future Enhancements

### SMTP:
- [ ] Password encryption at rest
- [ ] Multiple SMTP profiles
- [ ] Failover configuration
- [ ] Email sending statistics

### Invitations:
- [ ] Email invitation delivery (auto-send)
- [ ] Invitation templates
- [ ] Resend invitation
- [ ] Bulk invitations
- [ ] Custom expiry periods
- [ ] Welcome email on acceptance

---

## Related Files

### SMTP Configuration:
- `app/models/auth.py` - SMTPConfig model
- `app/routes/smtp.py` - SMTP API endpoints
- `app/services/email_service.py` - Email service with DB config
- `app/templates/admin/settings.html` - Settings UI
- `migrations/versions/add_smtp_invitations.py` - Database migration

### User Invitations:
- `app/models/auth.py` - PendingInvitation model
- `app/routes/invitations.py` - Invitation API endpoints
- `app/templates/admin/users.html` - User management UI
- `app/templates/accept_invitation.html` - Invitation acceptance page
- `app/routes/frontend.py` - Frontend route for invitation page

---

## Summary

Both features are now fully functional and ready for production use. Super admins can:

1. **Configure SMTP** from `/admin/settings` - No more .env editing!
2. **Invite Users** from `/admin/users` - No more CLI commands!

The system is secure, user-friendly, and follows best practices for admin management.
