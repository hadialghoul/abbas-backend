# Quick Setup Guide

## 1. Install Python Dependencies

Make sure you have Python 3.8+ installed, then:

```bash
cd backend
pip install -r requirements.txt
```

## 2. Configure Email Settings

Edit `primefix_backend/settings.py` and update these lines:

```python
EMAIL_HOST_USER = 'your-email@outlook.com'  # Your Microsoft email address
EMAIL_HOST_PASSWORD = 'your-password'  # Your email password (see below)
DEFAULT_FROM_EMAIL = 'your-email@outlook.com'  # Should match EMAIL_HOST_USER
```

**For Microsoft Email (Outlook/Hotmail):**

The settings are already configured for Microsoft email. You just need to:

1. **EMAIL_HOST_USER**: Enter your full Microsoft email address
   - Example: `yourname@outlook.com` or `yourname@hotmail.com`

2. **EMAIL_HOST_PASSWORD**: 
   - **If you DON'T have 2-factor authentication enabled:**
     - Just use your regular email password
   
   - **If you DO have 2-factor authentication enabled:**
     - Go to https://account.microsoft.com/security
     - Click "Advanced security options"
     - Scroll down to "App passwords"
     - Click "Create a new app password"
     - Use that generated app password here

3. **DEFAULT_FROM_EMAIL**: Should be the same as EMAIL_HOST_USER (the email address that will send the emails)

**For other email providers (Gmail, Yahoo, etc.):**
- Update `EMAIL_HOST` in settings.py to your provider's SMTP server
- Common SMTP servers:
  - Gmail: `smtp.gmail.com` (port 587)
  - Yahoo: `smtp.mail.yahoo.com` (port 587)

## 3. Run the Server

```bash
python manage.py runserver
```

The API will be available at: `http://localhost:8000/api/contact/`

**Note:** We don't store form submissions in a database - they're just sent directly to your email. The SQLite database file is only used by Django internally (you can ignore it).

## 4. Update Frontend API URL (if needed)

If your Django server runs on a different port or domain, update the API URL in `index.html`:

Look for this line in the JavaScript section:
```javascript
var apiUrl = 'http://localhost:8000/api/contact/';
```

Change it to match your server URL.

## 5. Test the Form

1. Open `index.html` in your browser (or serve it via a local server)
2. Fill out the contact form
3. Click "Submit Now"
4. Check the email inbox for `info@primefixusa.com`

## Troubleshooting

**Form submission fails:**
- Make sure Django server is running
- Check browser console for errors
- Verify API URL matches your Django server URL
- Check CORS settings in `settings.py`

**Email not sending:**
- Verify email credentials in `settings.py` (make sure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct)
- If using 2FA with Microsoft, make sure you're using an app password, not your regular password
- Check that DEFAULT_FROM_EMAIL matches your EMAIL_HOST_USER
- Check Django server logs for error messages (look for authentication errors)
- Test email configuration using Django shell:
  ```python
  python manage.py shell
  >>> from django.core.mail import send_mail
  >>> from django.conf import settings
  >>> send_mail('Test', 'Test message', settings.EMAIL_HOST_USER, ['info@primefixusa.com'])
  ```

