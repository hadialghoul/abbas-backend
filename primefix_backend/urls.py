"""
URL configuration for primefix_backend project.
"""
from django.urls import path, include
from django.http import JsonResponse


def root(request):
    return JsonResponse({'status': 'ok', 'service': 'primefix-backend'})


def healthz(request):
    return JsonResponse({'ok': True})

def handler400(request, exception):
    return JsonResponse({'error': 'Bad Request', 'detail': str(exception)}, status=400)

def handler500(request):
    return JsonResponse({'error': 'Internal Server Error'}, status=500)

urlpatterns = [
    path('', root),
    path('healthz/', healthz),
    path('api/', include('contact.urls')),
]

