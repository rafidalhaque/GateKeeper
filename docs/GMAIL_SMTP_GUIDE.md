# Gmail SMTP Configuration Guide

## Problem: "Incorrect authentication data" Error

If you're getting this error when testing SMTP with Gmail:
```
535 Incorrect authentication data
```

This means Gmail is rejecting your password. **You cannot use your regular Gmail password for SMTP!**

---

## Solution: Use Gmail App Password

### Step 1: Enable 2-Factor Authentication (Required)

1. Go to **Google Account**: https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Under "Signing in to Google", click **2-Step Verification**
4. Follow the prompts to set up 2FA if not already enabled
5. ✅ **You MUST have 2FA enabled to create App Passwords**

### Step 2: Create App Password

1. Go to **App Passwords**: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords (at the bottom)

2. Click **Select app** dropdown
   - Choose "Mail" or "Other (Custom name)"
   - If "Other", enter: "GateKeeper"

3. Click **Select device** dropdown
   - Choose your device or "Other"

4. Click **Generate**

5. **Copy the 16-character password** (looks like: `xxxx xxxx xxxx xxxx`)
   - ⚠️ **Important**: Save this password! You won't be able to see it again

### Step 3: Use App Password in GateKeeper

In the SMTP Configuration form, use these settings:

```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Username: your-email@gmail.com
Password: [paste the 16-character app password]
Sender Email: your-email@gmail.com
Sender Name: GateKeeper (or any name)
✓ Use TLS
✗ Use SSL
```

**Example Password**: (remove spaces when pasting)
```
abcd efgh ijkl mnop
```
Paste as: `abcdefghijklmnop`

---

## Full Configuration Examples

### Option 1: Gmail with TLS (Recommended)
```
Server: smtp.gmail.com
Port: 587
Username: yourname@gmail.com
Password: [16-char app password]
TLS: ✓ Enabled
SSL: ✗ Disabled
```

### Option 2: Gmail with SSL
```
Server: smtp.gmail.com
Port: 465
Username: yourname@gmail.com
Password: [16-char app password]
TLS: ✗ Disabled
SSL: ✓ Enabled
```

---

## Testing Your Configuration

1. Fill in the SMTP Configuration form in GateKeeper
2. Click **"Test Configuration"**
3. Enter your email address
4. Click **"Send Test Email"**
5. ✅ Check your inbox for the test email

If successful, you'll see:
```
✅ Test email sent successfully to your-email@gmail.com
```

---

## Troubleshooting

### Error: "Incorrect authentication data"
**Cause**: Using regular password instead of App Password

**Fix**:
1. Generate a new App Password (see Step 2 above)
2. Copy it exactly (remove any spaces)
3. Paste into the Password field
4. Test again

### Error: "Connection refused" or "Timeout"
**Cause**: Wrong port or firewall blocking

**Fix**:
- Use port **587** with TLS (most common)
- Or port **465** with SSL
- Check firewall settings
- Try disabling VPN temporarily

### Error: "Please enable 2-Step Verification"
**Cause**: 2FA not enabled on Google Account

**Fix**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Then create App Password

### Error: "App passwords option not available"
**Causes**:
1. 2FA not enabled → Enable it first
2. Using Google Workspace → Ask admin to enable
3. Using school/organization account → May be restricted

**Fix**:
- Personal Gmail: Enable 2FA, then retry
- Workspace: Contact your Google Workspace admin
- Consider using a personal Gmail account instead

---

## Alternative: Less Secure App Access (NOT Recommended)

⚠️ **Not recommended for security reasons**

If you absolutely cannot use App Passwords:

1. Go to: https://myaccount.google.com/lesssecureapps
2. Turn ON "Allow less secure apps"
3. Use your regular Gmail password

**WARNING**: This makes your account less secure. Use App Passwords instead!

---

## Other Email Providers

### SendGrid (Recommended for Production)
```
Server: smtp.sendgrid.net
Port: 587
Username: apikey
Password: [your SendGrid API key]
TLS: ✓ Enabled
```

### Mailgun
```
Server: smtp.mailgun.org
Port: 587
Username: [from Mailgun dashboard]
Password: [from Mailgun dashboard]
TLS: ✓ Enabled
```

### Amazon SES
```
Server: email-smtp.[region].amazonaws.com
Port: 587
Username: [SMTP username from SES]
Password: [SMTP password from SES]
TLS: ✓ Enabled
```

### Outlook/Hotmail
```
Server: smtp-mail.outlook.com
Port: 587
Username: your-email@outlook.com
Password: [your Outlook password]
TLS: ✓ Enabled
```

---

## Security Best Practices

1. ✅ **Always use App Passwords** for Gmail
2. ✅ **Use TLS/SSL** for encryption
3. ✅ **Store passwords securely** (database encryption)
4. ✅ **Test before saving** to verify credentials
5. ✅ **Use dedicated email accounts** for sending
6. ✅ **Enable 2FA** on all email accounts
7. ❌ **Never share App Passwords**
8. ❌ **Never commit passwords** to version control

---

## Quick Start Checklist

- [ ] Enable 2FA on Gmail account
- [ ] Create App Password for "Mail"
- [ ] Copy the 16-character password
- [ ] Go to GateKeeper → Settings → SMTP Configuration
- [ ] Enter Gmail SMTP details
- [ ] Paste App Password (no spaces)
- [ ] Click "Test Configuration"
- [ ] Check email inbox
- [ ] Click "Save Configuration"
- [ ] ✅ Done!

---

## Need Help?

### Check Gmail SMTP Status
Visit: https://www.google.com/appsstatus#hl=en&v=issue&sid=1&iid=5

### Gmail SMTP Documentation
https://support.google.com/mail/answer/7126229

### Common Ports Reference
- **Port 587** - TLS/STARTTLS (recommended)
- **Port 465** - SSL (legacy but works)
- **Port 25** - Plain (blocked by most ISPs)

---

## Summary

**For Gmail:**
1. Enable 2FA
2. Create App Password
3. Use `smtp.gmail.com:587` with TLS
4. Paste App Password in GateKeeper
5. Test and Save

**The 16-character App Password is the key!** Never use your regular Gmail password for SMTP.
