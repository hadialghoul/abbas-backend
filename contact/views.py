from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import BadHeaderError
from django.core.mail import get_connection, EmailMessage
from smtplib import SMTPException
import json
import logging
import queue
import threading
from urllib import error as urlerror
from urllib import request as urlrequest


logger = logging.getLogger(__name__)


def _accepted_with_email_issue():
    return JsonResponse({
        'success': True,
        'delivered': False,
        'message': 'Thank you for your submission! Your request was received and is being processed.'
    }, status=202)


def _send_email_smtp(subject, message):
    connection = get_connection(timeout=settings.EMAIL_TIMEOUT)
    email_message = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.RECIPIENT_EMAIL],
        connection=connection,
    )
    return email_message.send(fail_silently=False)


def _send_email_sendgrid(subject, message):
    if not settings.SENDGRID_API_KEY:
        raise RuntimeError('SENDGRID_API_KEY is not configured.')

    from_email = settings.SENDGRID_FROM_EMAIL or settings.DEFAULT_FROM_EMAIL
    payload = {
        'personalizations': [{'to': [{'email': settings.RECIPIENT_EMAIL}]}],
        'from': {'email': from_email},
        'subject': subject,
        'content': [{'type': 'text/plain', 'value': message}],
    }

    data = json.dumps(payload).encode('utf-8')
    req = urlrequest.Request(
        url='https://api.sendgrid.com/v3/mail/send',
        data=data,
        headers={
            'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urlrequest.urlopen(req, timeout=settings.EMAIL_TIMEOUT) as response:
            status_code = response.getcode()
    except urlerror.HTTPError as ex:
        response_body = ex.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'SendGrid HTTP {ex.code}: {response_body[:300]}')

    if status_code not in (200, 202):
        raise RuntimeError(f'SendGrid returned unexpected status {status_code}.')

    return 1


def _send_email(subject, message):
    provider = (settings.EMAIL_PROVIDER or 'smtp').lower()

    if provider == 'sendgrid':
        return _send_email_sendgrid(subject, message)
    if provider == 'smtp':
        return _send_email_smtp(subject, message)

    raise RuntimeError(f'Unsupported EMAIL_PROVIDER: {provider}')


def _send_email_with_capture(result_queue, subject, message):
    try:
        sent_count = _send_email(subject, message)
        result_queue.put({'ok': True, 'sent_count': sent_count})
    except Exception as ex:
        result_queue.put({'ok': False, 'error': str(ex)})


@csrf_exempt
def test_endpoint(request):
    """Test endpoint to verify routing works"""
    return JsonResponse({
        'success': True,
        'message': 'Backend is working!',
        'method': request.method
    })


@csrf_exempt
def submit_contact_form(request):
    """
    Handle contact form submissions and send email.
    """
    logger.info(f'=== VIEW CALLED === Method: {request.method}, Path: {request.path}, Content-Type: {request.content_type}')
    
    if request.method != 'POST':
        logger.warning(f'Wrong method: {request.method}')
        return JsonResponse({
            'success': False,
            'message': f'Only POST method is allowed. Received: {request.method}'
        }, status=405)
    
    try:
        # Parse JSON data from request body
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        data = json.loads(body)
        
        # Debug logging
        logger.info(f'Received data: {data}')
        
        # Extract form fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        service = data.get('service', '').strip()
        
        # Debug: log extracted values
        logger.info(f'Extracted - name: {name}, email: {email}, mobile: {mobile}, service: {service}')
        
        # Validate required fields
        if not name or not email or not mobile or not service:
            return JsonResponse({
                'success': False,
                'message': f'All fields are required. Received: name="{name}", email="{email}", mobile="{mobile}", service="{service}"'
            }, status=400)

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD or not settings.RECIPIENT_EMAIL:
            logger.error('Email settings are incomplete. Configure EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and RECIPIENT_EMAIL.')
            return JsonResponse({
                'success': False,
                'message': 'Email service is not configured correctly. Please contact support.'
            }, status=500)
        
        # Email subject
        subject = f'New Contact Form Submission from {name}'
        
        # Email message body
        message = f"""
        New contact form submission from your website:
        
        Name: {name}
        Email: {email}
        Mobile: {mobile}
        Service: {service}
        
        ---
        This is an automated message from your website contact form.
        """
        
        logger.info(f'Attempting to send email to {settings.RECIPIENT_EMAIL}')
        try:
            hard_timeout = min(max(int(settings.EMAIL_TIMEOUT), 3), 20)
            result_queue = queue.Queue(maxsize=1)
            sender_thread = threading.Thread(
                target=_send_email_with_capture,
                args=(result_queue, subject, message),
                daemon=True,
            )
            sender_thread.start()
            sender_thread.join(timeout=hard_timeout)

            if sender_thread.is_alive():
                logger.error('Email send exceeded timeout window and was aborted.')
                return _accepted_with_email_issue()

            try:
                result = result_queue.get_nowait()
            except queue.Empty:
                logger.error('Email send thread completed without returning a result.')
                return _accepted_with_email_issue()

            if not result.get('ok'):
                logger.error(f"Email send error: {result.get('error', 'Unknown error')}")
                return _accepted_with_email_issue()

            sent_count = result.get('sent_count', 0)
            if sent_count < 1:
                logger.error('SMTP call completed but no email was accepted by the server (sent_count=0).')
                return _accepted_with_email_issue()
        except Exception as ex:
            logger.error(f'Email send error: {str(ex)}', exc_info=True)
            return _accepted_with_email_issue()

        logger.info('Email sent successfully')

        return JsonResponse({
            'success': True,
            'message': 'Thank you for your submission! We will get back to you soon.'
        }, status=200)
            
    except json.JSONDecodeError as e:
        body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
        return JsonResponse({
            'success': False,
            'message': f'Invalid JSON data. Error: {str(e)}, Body: {body_str[:200]}'
        }, status=400)
    except (SMTPException, BadHeaderError) as e:
        logger.error(f'Email send error: {str(e)}', exc_info=True)
        return _accepted_with_email_issue()
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

