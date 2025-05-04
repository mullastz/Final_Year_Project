from django.shortcuts import render
from .models import CustomUser, VerificationToken
from .utils import send_verification_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_user(request):
    """
    Only staff (admin) users can register new users.
    """
    if not request.user.is_staff:
        return Response({'error': 'Only admin can create users.'}, status=403)

    data = request.data
    try:
        existing_user = CustomUser.objects.filter(email=data['email']).first()
        if existing_user:
            if not existing_user.is_active:
                return Response({'redirect': True, 'message': 'User exists but not verified. Please check your email.'})
            return Response({'error': 'User with this email already exists.'}, status=400)

        # Create new user
        user = CustomUser.objects.create_user(
            email=data['email'],
            password=data['password']
        )
        user.is_active = False
        user.save()

        send_verification_email(user)

        return Response({'message': 'User registered. Please check email to verify.'})

    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def verify_code(request):
    email = request.data.get('email')
    code = request.data.get('code')

    try:
        user = CustomUser.objects.get(email=email)
        token = VerificationToken.objects.filter(user=user, code=code, is_used=False).latest('created_at')

        if not token or not token.is_valid():
            return Response({'error': 'Invalid or expired code.'}, status=400)

        token.is_used = True
        token.save()

        if not user.is_active:
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully.'})

        refresh = RefreshToken.for_user(user)
        return Response({
            'redirect': True,
            'message': 'Login verified.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    except (CustomUser.DoesNotExist, VerificationToken.DoesNotExist):
        return Response({'error': 'User or code not found.'}, status=404)


@api_view(['POST'])
def login_request(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = CustomUser.objects.get(email=email)

        if not user.is_active:
            send_verification_email(user)
            return Response({
                'redirect': True,
                'message': 'Account not verified. Redirecting to verification page...',
                'email': user.email
            }, status=200)

        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=401)

        send_verification_email(user)
        return Response({'message': 'Verification code sent to email', 'email': user.email})

    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=404)


@api_view(['POST'])
def resend_code(request):
    email = request.data.get('email')
    try:
        user = CustomUser.objects.get(email=email)

        recent_token = VerificationToken.objects.filter(user=user).order_by('-created_at').first()
        if recent_token and timezone.now() - recent_token.created_at < timedelta(minutes=1):
            return Response({'error': 'Please wait before requesting another code.'}, status=429)

        send_verification_email(user)
        return Response({'message': 'Verification code resent.'})
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    return Response({
        "email": user.email,
    })
