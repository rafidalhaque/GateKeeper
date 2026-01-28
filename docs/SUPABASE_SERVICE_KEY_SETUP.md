# Supabase Service Role Key Configuration

## Issue
The invitation system requires a Supabase **service role key** to create users programmatically. The error "Supabase configuration not found" occurs when this key is missing.

## What are Supabase Keys?

Supabase provides different API keys for different purposes:

1. **anon (public) key** - Safe to use in frontend, limited permissions
2. **service_role key** - Full admin access, must be kept secret and only used in backend

## How to Get Your Service Role Key

### Step 1: Go to Supabase Dashboard
1. Open [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project: `ipqbrpbxazmhmyyfwqxc`

### Step 2: Navigate to API Settings
1. Click on **Settings** (gear icon) in the left sidebar
2. Click on **API** in the settings menu

### Step 3: Find the Service Role Key
1. Scroll down to the **Project API keys** section
2. You'll see two keys:
   - `anon` `public` - This is your `SUPABASE_KEY` (already configured)
   - `service_role` `secret` - **This is what you need!**
3. Click the **eye icon** to reveal the service_role key
4. Copy the entire key (it's a long JWT token starting with `eyJ...`)

### Step 4: Update Your .env File
1. Open `C:\Users\USER\PycharmProjects\GateKeeper\.env`
2. Find the line:
   ```
   SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
   ```
3. Replace `YOUR_SERVICE_ROLE_KEY_HERE` with the service_role key you just copied:
   ```
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Step 5: Restart Your Application
After updating the `.env` file, restart your Flask application:
```bash
# Stop the current server (Ctrl+C)
# Then restart:
flask --app run.py run
```

## Security Warning ⚠️

**NEVER** commit the service_role key to version control or expose it to the frontend!

- This key has full admin access to your Supabase project
- It can read, write, and delete any data
- It bypasses Row Level Security (RLS) policies
- Keep it secret, keep it safe!

## What This Key Is Used For

In the GateKeeper application, the service_role key is used to:
1. Create new admin users in Supabase Auth when invitations are sent
2. Update user email verification status
3. Perform admin operations on behalf of the system

## Testing After Configuration

After setting up the service_role key, test the invitation system:

1. Log in as Super Admin
2. Go to Settings > User Management
3. Click "Add User" / "Invite Admin"
4. Enter an email and select a role
5. You should receive a unique invitation link

If you still see errors, check:
- The service_role key is correct (no extra spaces)
- Your Flask app was restarted after updating `.env`
- The key starts with `eyJ` and is very long (several hundred characters)

## Alternative: Using Supabase CLI

If you have Supabase CLI installed:
```bash
supabase status
```

This will show your service_role key in the output.

## Need Help?

If you're still having issues:
1. Check the Flask logs for specific error messages
2. Verify your Supabase project is active
3. Make sure your Supabase project URL matches: `https://ipqbrpbxazmhmyyfwqxc.supabase.co`
