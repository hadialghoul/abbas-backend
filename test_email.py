"""
Quick script to test email configuration.
Run this to see the exact error message.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'primefix_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Testing email configuration...")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"RECIPIENT_EMAIL: {settings.RECIPIENT_EMAIL}")
print("-" * 50)

try:
    send_mail(
        subject='Test Email from Primefix Website',
        message='This is a test email from your website contact form.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.RECIPIENT_EMAIL],
        fail_silently=False,
    )
    print("SUCCESS! Email sent successfully!")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    print("\nCommon issues:")
    print("1. Wrong SMTP server - try smtp.office365.com or smtp-mail.outlook.com")
    print("2. Wrong password - make sure you're using the correct password")
    print("3. 2FA enabled - you may need an app password")
    print("4. Email provider - check if your domain uses Google Workspace (smtp.gmail.com)")

