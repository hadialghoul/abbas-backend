# How to Fix SMTP Authentication Error

## The Problem
Your Office 365 account has SMTP authentication disabled. This is a security setting that prevents apps from using basic SMTP authentication.

## Solution Options

### Option 1: Enable SMTP AUTH (If you have admin access)

1. Go to Microsoft 365 Admin Center: https://admin.microsoft.com
2. Go to **Settings** → **Org settings** → **Modern authentication**
3. Look for **SMTP AUTH** settings
4. Enable SMTP AUTH for your organization or specific users

**OR**

1. Go to Exchange Admin Center: https://admin.exchange.microsoft.com
2. Go to **Mail flow** → **Receive connectors**
3. Enable SMTP AUTH for your tenant

**Note:** This requires admin access to your Microsoft 365 tenant.

---

### Option 2: Use Gmail Instead (Easiest Solution)

If you have a Gmail account, you can use it to send emails:

1. **Update `settings.py`**:
   ```python
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
   EMAIL_HOST_PASSWORD = 'your-app-password'  # Gmail app password (see below)
   DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
   RECIPIENT_EMAIL = 'info@primefixusa.com'  # Still send to your business email
   ```

2. **Create Gmail App Password**:
   - Go to your Google Account: https://myaccount.google.com
   - Enable 2-Factor Authentication (if not already enabled)
   - Go to: https://myaccount.google.com/apppasswords
   - Generate an app password for "Mail"
   - Use that password in `EMAIL_HOST_PASSWORD`

3. **Benefits**:
   - Emails will be sent FROM your Gmail account
   - But will still be sent TO `info@primefixusa.com`
   - No admin access needed
   - Works immediately

---

### Option 3: Use SendGrid (Professional Solution)

SendGrid is a free email service (100 emails/day free):

1. Sign up at: https://sendgrid.com
2. Create an API key
3. Install SendGrid package:
   ```bash
   pip install sendgrid-django
   ```
4. Update settings.py (I can help with this if needed)

---

### Recommended Quick Fix

**Use Gmail (Option 2)** - It's the fastest and easiest solution that doesn't require admin access.

Would you like me to update the settings to use Gmail, or do you have admin access to enable SMTP AUTH?

