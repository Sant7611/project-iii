from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User extending AbstractUser.
    
    WHY AbstractUser?
    - Django's built-in User is 'final' — you can't easily extend it later.
    - If you ever need to add fields (bio, avatar, phone), you MUST do it
      BEFORE your first migration. That's why we set AUTH_USER_MODEL now.
    """
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    # AbstractUser already has: username, password, email, first_name, last_name,
    # is_staff, is_active, is_superuser, date_joined, last_login
    # So we DON'T redefine them. We only add what's extra.
    
    def __str__(self):
        return self.username
