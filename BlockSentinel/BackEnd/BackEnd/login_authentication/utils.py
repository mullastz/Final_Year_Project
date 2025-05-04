from django.core.mail import send_mail
from .models import VerificationToken

def send_verification_email(user):
    token = VerificationToken.objects.create(user=user)
    send_mail(
        'Your Email Verification Code',
        f'Your verification code is: {token.code}',
        'mullastz@gmail.com',
        [user.email],
        fail_silently=False,
    )