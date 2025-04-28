from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    supabase_uid = models.CharField(max_length=255, unique=True, null=True)
    email = models.EmailField(unique=True)
    
    # Additional fields for user profile
    profile_picture = models.URLField(max_length=500, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'custom_user'
        
    def __str__(self):
        return self.email
