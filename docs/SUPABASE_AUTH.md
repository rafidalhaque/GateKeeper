# Supabase Authentication Integration

This document explains the Supabase Auth integration for the GateKeeper admin panel.

## Overview

The admin authentication system now uses Supabase Auth with email/password login instead of manually pasting JWT tokens. This provides a more secure and user-friendly experience.

## Architecture

### Flow Diagram
```
User -> Login Form -> Supabase Auth -> Admin Verification -> Admin Panel
```

1. **User visits `/admin`** → Redirected to `/login` if not authenticated
2. **Login Form** → User enters email/password
3. **Supabase Auth** → Validates credentials and returns session
4. **Admin Verification** → Backend checks if user is authorized as admin
5. **Admin Panel** → User gains access to admin features

### Components

#### Frontend (Client-side)
- **Login Page** (`/login`): Supabase Auth form with email/password
- **Admin Pages** (`/admin/*`): Protected routes that require authentication
- **Base Template**: Handles session management and automatic token refresh

#### Backend (Server-side)
- **Auth Routes** (`/auth/*`): Session verification and admin authorization
- **HTML Protection**: Server-side redirects for unauthenticated requests
- **API Protection**: Existing JWT validation for API endpoints

## Setup Instructions

### 1. Supabase Project Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Go to **Settings** → **API** and copy:
   - Project URL
   - Anon public key  
   - JWT Secret (from **Settings** → **API** → **JWT Settings**)

### 2. Environment Configuration

Add to your `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 3. Database Setup

Run the database setup commands:
```bash
# Initialize permissions
flask seed-permissions

# Initialize roles  
flask seed-roles

# Create your first admin user
flask create-admin --email admin@yourcompany.com --name "Admin User"
```

### 4. Supabase Auth Setup

In your Supabase dashboard:

1. Go to **Authentication** → **Users**
2. Click **Invite user** or **Add user**
3. Use the same email as your admin user
4. Set a password for the user
5. The user can now log in to the admin panel

## Usage

### Creating Admin Users

#### Method 1: CLI + Supabase Dashboard (Recommended)
```bash
# 1. Create admin record in GateKeeper database
flask create-admin --email newuser@company.com --name "New User"

# 2. Create auth user in Supabase (via dashboard or API)
# - Go to Supabase Auth dashboard
# - Add user with same email
# - Set password
```

#### Method 2: Super Admin
```bash
# Create a super admin (has all permissions)
flask create-super-admin --email superadmin@company.com --name "Super Admin"
```

### User Login Flow

1. **Direct Access**: User visits `/admin/events` 
2. **Redirect**: Automatically redirected to `/login?next=/admin/events`
3. **Authentication**: User enters email/password
4. **Verification**: System verifies user is an authorized admin
5. **Access Granted**: User is redirected back to `/admin/events`

### Session Management

- **Automatic Refresh**: Tokens are refreshed automatically by Supabase
- **Logout**: Clears both Supabase session and localStorage
- **Persistence**: Sessions persist across browser tabs/windows
- **Expiration**: Users are automatically redirected to login when sessions expire

## Security Features

### Server-Side Protection
- All admin HTML routes require authentication
- Unauthenticated requests are redirected to login
- Admin verification ensures only authorized users access admin features

### Client-Side Security
- Automatic token refresh prevents expired sessions
- Secure session management via Supabase
- Logout clears all client-side tokens

### Role-Based Access Control
- Super admins bypass all permission checks
- Regular admins are assigned specific roles with limited permissions
- Permissions are checked for each API endpoint

## API Authentication

The existing API authentication continues to work:

```javascript
// Make authenticated API requests
const response = await authFetch('/api/events');
```

The `authFetch` function automatically:
- Gets fresh tokens from Supabase
- Adds Authorization header
- Handles 401 responses by redirecting to login

## Troubleshooting

### Common Issues

1. **"User not authorized as admin"**
   - Ensure the admin user exists in the database: `flask create-admin`
   - Check that the email matches exactly between Supabase and database

2. **"Authentication required" loop**
   - Check Supabase configuration in `.env`
   - Verify JWT secret is correct
   - Clear browser localStorage and try again

3. **Token validation errors**
   - Ensure `SUPABASE_JWT_SECRET` matches your Supabase project
   - Check that the user exists in Supabase Auth

### Debug Commands

```bash
# Check admin users
flask shell
>>> from app.models.auth import AdminUser
>>> AdminUser.query.all()

# Test configuration
python test_auth_setup.py
```

## Migration from Old System

If upgrading from the manual JWT system:

1. **Backup existing admin users**
2. **Run new database migrations**: The system will handle existing users
3. **Create Supabase accounts**: For each existing admin, create a corresponding Supabase auth user
4. **Test login flow**: Verify each admin can log in with email/password

## Development Notes

### Key Files
- `app/routes/auth.py` - Auth API endpoints
- `app/routes/frontend.py` - HTML route protection  
- `app/utils/auth.py` - Authentication decorators
- `app/templates/login.html` - Login form
- `app/templates/admin/base.html` - Session management

### Configuration
- Supabase config is passed to all admin templates
- Templates initialize Supabase client with project credentials
- Auth state is managed globally in JavaScript

This integration provides a robust, scalable authentication system suitable for production use.
