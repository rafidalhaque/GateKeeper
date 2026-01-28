# 🔧 URGENT: Supabase Service Key Configuration Required

## Problem
The invitation system is failing with error:
```
"error": "Failed to create invitation: Supabase configuration not found"
```

## Root Cause
The `SUPABASE_SERVICE_KEY` environment variable is set to a placeholder value instead of your actual service role key.

## Solution: Get Your Service Role Key from Supabase

### Quick Steps:

1. **Open Supabase Dashboard**
   - Go to: https://supabase.com/dashboard
   - Select your project: `ipqbrpbxazmhmyyfwqxc`

2. **Navigate to API Settings**
   - Click **Settings** (⚙️ icon in left sidebar)
   - Click **API** in the settings menu

3. **Copy Service Role Key**
   - Scroll to **Project API keys** section
   - Find the `service_role` key (marked as `secret`)
   - Click the **eye icon** (👁️) to reveal the key
   - Click **Copy** to copy the entire key
   - It should look like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlw...` (very long)

4. **Update .env File**
   - Open: `C:\Users\USER\PycharmProjects\GateKeeper\.env`
   - Find line: `SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY_HERE`
   - Replace with: `SUPABASE_SERVICE_KEY=eyJhbGci...` (paste the key you copied)
   - Save the file

5. **Restart Flask Application**
   ```bash
   # Stop the running Flask server (Ctrl+C in terminal)
   # Then start it again:
   flask --app run.py run
   ```

6. **Verify Configuration**
   ```bash
   python verify_supabase.py
   ```
   
   You should see:
   ```
   ✅ All Supabase configuration is correct!
   🎉 You can now use the invitation system to create admin users.
   ```

## What is Service Role Key?

| Key Type | Purpose | Where to Use |
|----------|---------|--------------|
| **anon** (public) | Limited access, safe for frontend | Already configured ✅ |
| **service_role** (secret) | Full admin access, backend only | **Missing - needs setup** ❌ |

The service_role key is needed to:
- ✨ Create users in Supabase Auth (for invitations)
- ✨ Update user passwords
- ✨ Verify user emails programmatically
- ✨ Manage admin operations

## Security Note 🔒

**NEVER** share or commit the service_role key to version control!
- It has full admin access to your Supabase project
- It can bypass all Row Level Security (RLS) policies
- It should only be used in secure backend code

## After Configuration

Once configured, you can:
1. Go to Settings → User Management in the admin panel
2. Click "Add User" / "Invite Admin"
3. Enter email and select role
4. System will create Supabase user and generate invitation link
5. Copy the link and send to the new admin
6. They can set their password using the link

## Still Having Issues?

Run the diagnostic script:
```bash
python verify_supabase.py
```

Check Flask logs for specific errors:
- Look for "Supabase" in error messages
- Check if service key is being read correctly

## Files Created to Help You:
- ✅ `SUPABASE_SERVICE_KEY_SETUP.md` - Detailed setup guide
- ✅ `verify_supabase.py` - Configuration verification script
- ✅ This file - Quick reference

## Need the Service Key Screenshot Location?

In Supabase Dashboard:
```
Dashboard → Settings (⚙️) → API → Project API keys → service_role (secret)
                                                         ↑
                                                    Click eye icon here
```
