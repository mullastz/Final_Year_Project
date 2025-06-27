from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework import status
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from login_authentication.models import CustomUser  # use your actual model import
from login_authentication.models import validate_password_strength
from .serializers import AdminListSerializer, AdminUpdateSerializer
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_admin_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_admin_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get fields from request
    new_email = request.data.get('email')
    new_name = request.data.get('name')

    # Update email in user model
    if new_email and new_email != user.email:
        user.email = new_email
        user.username = new_email  # optional: email is username

    # Save display name in profile
    if new_name:
        profile.display_name = new_name

    # Handle profile photo upload
    if 'photo' in request.FILES:
        profile.profile_photo = request.FILES['photo']

    user.save()
    profile.save()

    return Response({'status': 'Profile updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    current = request.data.get('current_password')
    new = request.data.get('new_password')
    confirm = request.data.get('confirm_password')

    if not current or not new or not confirm:
        return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify current password
    if not user.check_password(current):
        return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)

    if new != confirm:
        return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password_strength(new)  # Reuse your existing validator
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new)
    user.save()

    # Invalidate session / JWT
    logout(request)

    return Response({'success': 'Password changed successfully. Please log in again.'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_admins(request):
    admins = CustomUser.objects.filter(is_staff=True)
    serializer = AdminListSerializer(admins, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_admin(request, id):
    try:
        admin = CustomUser.objects.get(id=id, is_staff=True)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=404)

    serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': 'Admin updated successfully'})
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_admin(request, id):
    try:
        admin = CustomUser.objects.get(id=id, is_staff=True)
        admin.delete()
        return Response({'success': 'Admin deleted'})
    except CustomUser.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def create_admin_user(request):
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=403)

    data = request.data
    try:
        if CustomUser.objects.filter(email=data['email']).exists():
            return Response({'error': 'User with this email already exists.'}, status=400)

        user = CustomUser.objects.create_user(
            email=data['email'],
            password=data['password'],
            admin_name=data.get('name', ''),
            role=data.get('role', ''),
            is_active=True,
            is_staff=True  # Or only for SuperAdmins if you want to restrict
        )
        return Response({'success': 'Admin created successfully.'}, status=201)

    except Exception as e:
        return Response({'error': str(e)}, status=500)    
    
@api_view(['GET'])
def get_csrf_token(request):
    token = get_token(request)
    return Response({'csrfToken': token})

