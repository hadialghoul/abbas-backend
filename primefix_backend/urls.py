"""
URL configuration for primefix_backend project.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('contact.urls')),
]

