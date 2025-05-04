# serializers.py
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email']
        read_only_fields = ['is_active', 'is_staff', 'is_superuser']

class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '_all_'  # Used only by staff internally

    