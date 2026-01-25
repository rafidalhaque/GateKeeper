# Quick Setup Guide: SMTP & User Invitations

## Prerequisites

1. Supabase project with Auth enabled
2. Service role key from Supabase dashboard
3. Super admin account

## Step 1: Update Environment Variables

Add to your `.env` file:

```env
# Existing Supabase config
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# NEW: Service role key (required for invitations)
SUPABASE_SERVICE_KEY=your-service-role-key

# NEW: Frontend URL (for invitation links)
FRONTEND_URL=http://localhost:5000
```

### Where to find Supabase Service Key:
1. Go to Supabase Dashboard
2. Project Settings → API
3. Copy "service_role" key (secret)

## Step 2: Run Database Migration

```bash
cd C:/Users/USER/PycharmProjects/GateKeeper

# Option 1: Flask-Migrate
flask --app run.py db upgrade

# Option 2: Alembic
alembic upgrade head
```

This creates two new tables:
- `smtp_config` - For email configuration
- `pending_invitations` - For user invitations

## Step 3: Test SMTP Configuration (Super Admin Only)

1. Login as super admin
2. Navigate to: `http://localhost:5000/admin/settings`
3. Scroll to "SMTP Configuration" section
4. Fill in your SMTP details:

### Gmail Example:
```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Username: your-email@gmail.com
Password: your-app-password
Sender Email: noreply@yourdomain.com
Sender Name: GateKeeper
☑ Use TLS
☐ Use SSL
```

5. Click "Test Configuration"
6. Enter your email to receive test
7. Click "Save Configuration"

✅ **Success!** All emails now use database config instead of .env

## Step 4: Invite Your First Admin User

1. Navigate to: `http://localhost:5000/admin/users`
2. Click "Add User" button
3. Fill in the form:
   - **Email**: newadmin@example.com
   - **Name**: New Admin
   - **Role**: Event Admin (or any role)
4. Click "Send Invitation"
5. **Copy the invitation link** from the modal
6. Share link with the new admin

### What happens:
- ✅ User created in Supabase Auth
- ✅ Invitation token generated
- ✅ Expires in 7 days
- ✅ Ready to be accepted!

## Step 5: New Admin Accepts Invitation

1. New admin opens invitation link
2. Sees invitation details
3. Sets password (min 8 chars)
4. Confirms password
5. Clicks "Accept Invitation & Set Password"
6. **Email automatically verified!**
7. Redirected to login page
8. Can now login with email + password

## Verification

### Check SMTP Config:
```bash
# As super admin, GET request:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/smtp/config
```

Should return your SMTP configuration.

### Check Invitations:
```bash
# As super admin, GET request:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:5000/api/invitations/
```

Should return list of pending invitations.

### Check New User:
1. New admin logs in at `/login`
2. Navigate to `/admin`
3. Should see dashboard
4. Role-based permissions applied

## Common Issues

### Issue: "SUPABASE_SERVICE_KEY not found"
**Solution**: Add service role key to .env and restart server

### Issue: "Failed to create Supabase user"
**Solutions**:
- Verify SUPABASE_URL is correct
- Verify SUPABASE_SERVICE_KEY is valid
- Check service key has user management permissions
- Check Supabase project is active

### Issue: "Invitation link not working"
**Solutions**:
- Check token hasn't expired (7 days)
- Verify FRONTEND_URL in .env matches actual URL
- Check invitation status in database

### Issue: "SMTP Configuration not saving"
**Solutions**:
- Verify you're logged in as super admin
- Check database migration ran successfully
- Verify all required fields filled
- Test configuration before saving

## Testing Checklist

- [ ] Environment variables updated
- [ ] Database migration successful
- [ ] SMTP configuration created
- [ ] SMTP test email received
- [ ] Invitation created
- [ ] Invitation link copied
- [ ] New admin accepted invitation
- [ ] New admin can login
- [ ] New admin has correct role
- [ ] New admin email is verified

## Production Deployment

### Additional Steps for Production:

1. **Use SSL for SMTP** (port 465) if available
2. **Use production email service** (not Gmail personal)
3. **Set strong passwords** for SMTP accounts
4. **Use environment variables** for sensitive data
5. **Enable SMTP encryption** in database (TODO)
6. **Monitor invitation expiry** and clean up old records
7. **Use HTTPS** for FRONTEND_URL
8. **Enable rate limiting** on invitation endpoints

### Recommended SMTP Providers:
- **SendGrid** - 100 emails/day free
- **Mailgun** - 5,000 emails/month free
- **Amazon SES** - Very cheap, reliable
- **Postmark** - Premium, transactional focus

## Next Steps

1. **Invite your team** using the invitation system
2. **Configure roles** for different permission levels
3. **Setup email templates** for better emails
4. **Monitor email delivery** in SMTP dashboard
5. **Review invitation logs** in database

## Support

For detailed documentation, see:
- `docs/SMTP_AND_INVITATIONS.md` - Full feature documentation
- `docs/USER_MANAGEMENT_FIX.md` - User management guide
- `docs/ROLE_MANAGEMENT_FIX.md` - Role management guide

---

**🎉 Congratulations!** Your GateKeeper instance now has:
- ✅ Database-driven SMTP configuration
- ✅ Frontend user invitation system
- ✅ Automatic email verification
- ✅ Super admin-only controls

No more CLI commands or .env editing for these tasks!
