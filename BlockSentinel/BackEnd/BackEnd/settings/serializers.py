from rest_framework import serializers
from .models import UserProfile
from login_authentication.models import CustomUser  # or wherever your CustomUser is

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    display_name = serializers.CharField()         # ✅ FIXED (no source)
    profile_photo = serializers.ImageField()       # ✅ FIXED (no source)

    class Meta:
        model = UserProfile
        fields = ['user', 'display_name', 'profile_photo']

class AdminListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='admin_name')

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'role', 'is_active']

class AdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['admin_name', 'email', 'role', 'is_active', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)