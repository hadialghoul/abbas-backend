"""
URL configuration for primefix_backend project.
"""
from django.urls import path, include
from django.http import JsonResponse

def handler400(request, exception):
    return JsonResponse({'error': 'Bad Request', 'detail': str(exception)}, status=400)

def handler500(request):
    return JsonResponse({'error': 'Internal Server Error'}, status=500)

urlpatterns = [
    path('api/', include('contact.urls')),
]

