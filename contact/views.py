from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
import json


@csrf_exempt
@require_http_methods(["POST"])
def submit_contact_form(request):
    """
    Handle contact form submissions and send email.
    """
    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        
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
        return JsonResponse({
            'success': False,
            'message': f'Invalid JSON data. Error: {str(e)}, Body: {request.body.decode("utf-8")[:200]}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }, status=500)

