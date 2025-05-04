# serializers.py

from rest_framework import serializers
from .models import RegisteredSystem, SystemAdmin

class SystemAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemAdmin
        fields = ['name', 'email']

class RegisteredSystemSerializer(serializers.ModelSerializer):
    admins = SystemAdminSerializer(many=True, required=False)

    class Meta:
        model = RegisteredSystem
        fields = '__all__'
        extra_kwargs = {
            'profile_photo': {'required': False, 'allow_null': True},
        }    

    def create(self, validated_data):
        admins_data = validated_data.pop('admins', [])
        profile_photo = validated_data.pop('profile_photo', None)
        
        # Use a default profile photo if none provided
        if not profile_photo:
            profile_photo = 'path_to_default_image.jpg'  # Set a default image path here

        registered_system = RegisteredSystem.objects.create(profile_photo=profile_photo, **validated_data)
        
        # Create admins only if provided
        for admin_data in admins_data:
            SystemAdmin.objects.create(registered_system=registered_system, **admin_data)
        
        return registered_system
