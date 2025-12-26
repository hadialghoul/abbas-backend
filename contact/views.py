from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json


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
    # Log that we received the request
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f'Request received - Method: {request.method}, Path: {request.path}')
    
    if request.method != 'POST':
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
        import logging
        logger = logging.getLogger(__name__)
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
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.RECIPIENT_EMAIL],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your submission! We will get back to you soon.'
            }, status=200)
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Email send error: {str(e)}')
            
            # Return error details (remove in production for security)
            return JsonResponse({
                'success': False,
                'message': f'Failed to send email: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError as e:
        body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else str(request.body)
        return JsonResponse({
            'success': False,
            'message': f'Invalid JSON data. Error: {str(e)}, Body: {body_str[:200]}'
        }, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)

