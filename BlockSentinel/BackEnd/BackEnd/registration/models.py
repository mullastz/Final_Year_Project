# models.py

from django.db import models # type: ignore
import uuid



class RegisteredSystem(models.Model):
    system_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    display_id = models.CharField(max_length=20, unique=True)  # e.g., SYS-e4b16a89
    name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='system_profiles/', null=True, blank=True,  default='system_profiles/default.jpg')
    url = models.URLField()
    data_type = models.CharField(max_length=255)
    system_type = models.CharField(max_length=255)
    num_admins = models.IntegerField()
    date_registered = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.name} ({self.display_id})"


class SystemAdmin(models.Model):
    registered_system = models.ForeignKey(RegisteredSystem, related_name='admins', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.registered_system.name}"
