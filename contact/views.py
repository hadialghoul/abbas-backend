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
import socket
import smtplib
import time
from urllib import parse as urlparse
from urllib import request as urlrequest
from urllib import error as urlerror

from .models import ContactSubmission


logger = logging.getLogger(__name__)


def _accepted_with_email_issue():
    return JsonResponse({
        'success': True,
        'delivered': False,
        'message': 'Thank you for your submission! Your request was received and is being processed.'
    }, status=202)


def _send_email_smtp(subject, message, reply_to_email=None):
    connection = get_connection(timeout=settings.EMAIL_TIMEOUT)
    reply_to = [reply_to_email] if reply_to_email else None
    email_message = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.RECIPIENT_EMAIL],
        connection=connection,
        reply_to=reply_to,
    )
    return email_message.send(fail_silently=False)


def _get_graph_access_token():
    token_url = (
        f'https://login.microsoftonline.com/{settings.MS_GRAPH_TENANT_ID}'
        '/oauth2/v2.0/token'
    )
    token_data = urlparse.urlencode({
        'client_id': settings.MS_GRAPH_CLIENT_ID,
        'client_secret': settings.MS_GRAPH_CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }).encode('utf-8')

    request_obj = urlrequest.Request(
        token_url,
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )

    with urlrequest.urlopen(request_obj, timeout=settings.EMAIL_TIMEOUT) as response:
        payload = json.loads(response.read().decode('utf-8'))

    access_token = payload.get('access_token')
    if not access_token:
        raise RuntimeError('Microsoft Graph token response did not include access_token.')

    return access_token


def _send_email_graph(subject, message, reply_to_email=None):
    access_token = _get_graph_access_token()
    sender_user = urlparse.quote(settings.MS_GRAPH_SENDER_USER)
    send_url = f'https://graph.microsoft.com/v1.0/users/{sender_user}/sendMail'

    message_payload = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': message,
            },
            'toRecipients': [
                {'emailAddress': {'address': settings.RECIPIENT_EMAIL}}
            ],
        },
        'saveToSentItems': True,
    }

    if reply_to_email:
        message_payload['message']['replyTo'] = [
            {'emailAddress': {'address': reply_to_email}}
        ]

    request_obj = urlrequest.Request(
        send_url,
        data=json.dumps(message_payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urlrequest.urlopen(request_obj, timeout=settings.EMAIL_TIMEOUT) as response:
            status_code = response.getcode()
    except urlerror.HTTPError as ex:
        response_body = ex.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'Microsoft Graph sendMail failed with HTTP {ex.code}: {response_body[:300]}')

    if status_code not in (200, 202):
        raise RuntimeError(f'Microsoft Graph sendMail returned unexpected status {status_code}.')

    return 1


def _send_email_brevo(subject, message, reply_to_email=None):
    payload = {
        'sender': {
            'name': settings.BREVO_SENDER_NAME,
            'email': settings.BREVO_SENDER_EMAIL,
        },
        'to': [
            {'email': settings.RECIPIENT_EMAIL}
        ],
        'subject': subject,
        'textContent': message,
    }

    if reply_to_email:
        payload['replyTo'] = {'email': reply_to_email}

    request_obj = urlrequest.Request(
        'https://api.brevo.com/v3/smtp/email',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'api-key': settings.BREVO_API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        method='POST',
    )

    try:
        with urlrequest.urlopen(request_obj, timeout=settings.EMAIL_TIMEOUT) as response:
            status_code = response.getcode()
    except urlerror.HTTPError as ex:
        response_body = ex.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'Brevo send failed with HTTP {ex.code}: {response_body[:300]}')

    if status_code not in (200, 201, 202):
        raise RuntimeError(f'Brevo send returned unexpected status {status_code}.')

    return 1


def _send_email(subject, message, reply_to_email=None):
    provider = (settings.EMAIL_PROVIDER or 'smtp').lower()

    if provider == 'brevo':
        return _send_email_brevo(subject, message, reply_to_email=reply_to_email)

    if provider == 'graph' or settings.USE_MICROSOFT_GRAPH:
        return _send_email_graph(subject, message, reply_to_email=reply_to_email)

    return _send_email_smtp(subject, message, reply_to_email=reply_to_email)


def _email_transport_is_configured():
    provider = (settings.EMAIL_PROVIDER or 'smtp').lower()

    if provider == 'brevo':
        return bool(settings.BREVO_API_KEY and settings.BREVO_SENDER_EMAIL and settings.RECIPIENT_EMAIL)

    if provider == 'graph' or settings.USE_MICROSOFT_GRAPH:
        return True

    return bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD and settings.RECIPIENT_EMAIL)


def _send_email_with_capture(result_queue, subject, message, reply_to_email):
    try:
        sent_count = _send_email(subject, message, reply_to_email=reply_to_email)
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
def smtp_diagnostic(request):
    """Run step-by-step SMTP diagnostics to find the failing stage on the runtime host."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Only GET method is allowed.'}, status=405)

    token = request.GET.get('token', '')
    if not settings.SMTP_DIAG_TOKEN or token != settings.SMTP_DIAG_TOKEN:
        return JsonResponse({'success': False, 'message': 'Unauthorized.'}, status=401)

    host = settings.EMAIL_HOST
    port = int(settings.EMAIL_PORT)
    timeout = int(settings.EMAIL_TIMEOUT)
    result = {
        'success': False,
        'host': host,
        'port': port,
        'timeout': timeout,
        'use_tls': bool(settings.EMAIL_USE_TLS),
        'use_ssl': bool(settings.EMAIL_USE_SSL),
        'stages': [],
    }

    smtp_client = None
    start_time = time.time()

    try:
        dns_start = time.time()
        resolved = socket.getaddrinfo(host, port)
        result['stages'].append({
            'stage': 'dns_resolve',
            'ok': True,
            'elapsed_ms': int((time.time() - dns_start) * 1000),
            'ip_count': len(resolved),
        })

        connect_start = time.time()
        if settings.EMAIL_USE_SSL:
            smtp_client = smtplib.SMTP_SSL(host=host, port=port, timeout=timeout)
        else:
            smtp_client = smtplib.SMTP(host=host, port=port, timeout=timeout)

        code, _ = smtp_client.ehlo()
        result['stages'].append({
            'stage': 'connect_ehlo',
            'ok': True,
            'elapsed_ms': int((time.time() - connect_start) * 1000),
            'smtp_code': code,
        })

        if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            tls_start = time.time()
            code, _ = smtp_client.starttls()
            smtp_client.ehlo()
            result['stages'].append({
                'stage': 'starttls',
                'ok': True,
                'elapsed_ms': int((time.time() - tls_start) * 1000),
                'smtp_code': code,
            })

        login_start = time.time()
        smtp_client.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        result['stages'].append({
            'stage': 'auth_login',
            'ok': True,
            'elapsed_ms': int((time.time() - login_start) * 1000),
        })

        result['success'] = True
        result['message'] = 'SMTP diagnostic completed successfully.'
        result['total_elapsed_ms'] = int((time.time() - start_time) * 1000)
        return JsonResponse(result, status=200)
    except Exception as ex:
        result['message'] = 'SMTP diagnostic failed.'
        result['error_type'] = type(ex).__name__
        result['error'] = str(ex)
        result['total_elapsed_ms'] = int((time.time() - start_time) * 1000)
        logger.error('SMTP diagnostic failed', exc_info=True)
        return JsonResponse(result, status=200)
    finally:
        if smtp_client is not None:
            try:
                smtp_client.quit()
            except Exception:
                pass


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

        submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            service=service,
        )

        if not _email_transport_is_configured():
            logger.error('Email settings are incomplete. Configure SMTP credentials or Microsoft Graph credentials and RECIPIENT_EMAIL.')
            submission.delivery_status = ContactSubmission.DELIVERY_FAILED
            submission.delivery_error = 'Email settings are incomplete.'
            submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
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
                args=(result_queue, subject, message, email),
                daemon=True,
            )
            sender_thread.start()
            sender_thread.join(timeout=hard_timeout)

            if sender_thread.is_alive():
                logger.error('Email send exceeded timeout window and was aborted.')
                submission.delivery_status = ContactSubmission.DELIVERY_FAILED
                submission.delivery_error = 'Email send exceeded timeout window.'
                submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
                return _accepted_with_email_issue()

            try:
                result = result_queue.get_nowait()
            except queue.Empty:
                logger.error('Email send thread completed without returning a result.')
                submission.delivery_status = ContactSubmission.DELIVERY_FAILED
                submission.delivery_error = 'Email send thread completed without returning a result.'
                submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
                return _accepted_with_email_issue()

            if not result.get('ok'):
                error_message = result.get('error', 'Unknown error')
                logger.error(f"Email send error: {error_message}")
                submission.delivery_status = ContactSubmission.DELIVERY_FAILED
                submission.delivery_error = error_message
                submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
                return _accepted_with_email_issue()

            sent_count = result.get('sent_count', 0)
            if sent_count < 1:
                logger.error('SMTP call completed but no email was accepted by the server (sent_count=0).')
                submission.delivery_status = ContactSubmission.DELIVERY_FAILED
                submission.delivery_error = 'SMTP call completed but no email was accepted by the server.'
                submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
                return _accepted_with_email_issue()
        except Exception as ex:
            logger.error(f'Email send error: {str(ex)}', exc_info=True)
            submission.delivery_status = ContactSubmission.DELIVERY_FAILED
            submission.delivery_error = str(ex)
            submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])
            return _accepted_with_email_issue()

        submission.delivery_status = ContactSubmission.DELIVERY_SENT
        submission.delivery_error = ''
        submission.save(update_fields=['delivery_status', 'delivery_error', 'updated_at'])

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

