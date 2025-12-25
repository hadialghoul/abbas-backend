# GoDaddy Email Setup Instructions

Since your email is hosted on GoDaddy, you need to enable SMTP Authentication first.

## Step 1: Enable SMTP Authentication in GoDaddy

1. **Log in to GoDaddy Email & Office Dashboard:**
   - Go to: https://sso.godaddy.com
   - Sign in with your GoDaddy account

2. **Access Email Settings:**
   - Go to your Email & Office Dashboard
   - Find your email account: `info@primefixusa.com`
   - Click **"Manage"** next to the email account

3. **Enable SMTP Authentication:**
   - Scroll down to **"Account information"** section
   - Click on **"Advanced Settings"**
   - Find **"SMTP Authentication"**
   - Toggle it to **"On"**
   - Click **"Continue"** to save

## Step 2: Test Email

After enabling SMTP AUTH, test the email:

```bash
cd backend
python test_email.py
```

Or try submitting the contact form on your website.

## If It Still Doesn't Work

If you still get authentication errors, try using GoDaddy's own SMTP server. Update `settings.py`:

```python
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
```

Then test again.

## Video Guide

For visual instructions, see: https://www.youtube.com/watch?v=E4HPOhTY7fY

