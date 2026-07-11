from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_endpoint, name='test_endpoint'),
    path('diag/smtp/', views.smtp_diagnostic, name='smtp_diagnostic'),
    path('contact/', views.submit_contact_form, name='submit_contact_form'),
]

