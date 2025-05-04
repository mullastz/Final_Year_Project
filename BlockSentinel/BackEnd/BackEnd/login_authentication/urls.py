# login_authentication/urls.py

from django.urls import path
from .views import register_user, verify_code, login_request, resend_code

urlpatterns = [
    path('register/', register_user),
    path('verify/', verify_code),
    path('login/', login_request),
    path('resend-code/', resend_code),
]
