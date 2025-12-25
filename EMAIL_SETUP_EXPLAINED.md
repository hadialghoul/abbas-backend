# Email Configuration Explained (Microsoft Email)

## What are these settings?

**EMAIL_HOST_USER**: This is your email address that will be used to send emails
- Example: `info@primefixusa.com` or `yourname@outlook.com`
- This is the email account that will send the contact form submissions

**EMAIL_HOST_PASSWORD**: This is the password for the email account above
- If you DON'T have 2-factor authentication: Use your regular email password
- If you HAVE 2-factor authentication: You need to create an "app password" (see instructions below)

## Quick Setup for Microsoft Email (Outlook/Hotmail)

1. Open `primefix_backend/settings.py`

2. Find these lines (around line 135-139):
   ```python
   EMAIL_HOST_USER = ''  # Your Microsoft email address
   EMAIL_HOST_PASSWORD = ''  # Your Microsoft email password
   DEFAULT_FROM_EMAIL = 'info@primefixusa.com'
   ```

3. Fill them in like this:
   ```python
   EMAIL_HOST_USER = 'info@primefixusa.com'  # Your Microsoft email address
   EMAIL_HOST_PASSWORD = 'YourActualPassword123'  # Your email password
   DEFAULT_FROM_EMAIL = 'info@primefixusa.com'  # Should match EMAIL_HOST_USER
   ```

## Do I need an "app password"?

**You only need an app password if you have 2-factor authentication (2FA) enabled on your Microsoft account.**

### If you DON'T have 2FA:
- Just use your regular email password
- That's it! Simple as that.

### If you DO have 2FA:
You need to create an "app password" because Microsoft requires it for apps that send emails:

1. Go to: https://account.microsoft.com/security
2. Click on "Advanced security options"
3. Scroll down to find "App passwords"
4. Click "Create a new app password"
5. Give it a name (like "Website Contact Form")
6. Copy the generated password (it will look like: `abcd-efgh-ijkl-mnop`)
7. Use this app password in `EMAIL_HOST_PASSWORD` (NOT your regular password)

## Example Configuration

Here's a complete example:

```python
EMAIL_HOST_USER = 'info@primefixusa.com'
EMAIL_HOST_PASSWORD = 'YourPassword123'  # or app password if 2FA enabled
DEFAULT_FROM_EMAIL = 'info@primefixusa.com'
RECIPIENT_EMAIL = 'info@primefixusa.com'  # Where form submissions will be sent
```

## Important Notes

- **EMAIL_HOST_USER** and **DEFAULT_FROM_EMAIL** should be the same email address
- **RECIPIENT_EMAIL** is where the form submissions will be sent (can be the same or different)
- The settings are already configured for Microsoft email (`smtp-mail.outlook.com`)
- No need to change EMAIL_HOST if you're using Microsoft/Outlook

## Testing

After setting up, you can test if it works by running:

```bash
python manage.py runserver
```

Then submit the contact form on your website. Check the email inbox for `info@primefixusa.com` to see if you received the submission.

