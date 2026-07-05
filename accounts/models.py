from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
from django.utils import timezone
from datetime import timedelta

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

class APIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(unique=True, max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)


    def generate_token(self):
        token = secrets.token_urlsafe(20)
        return token
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            self.expires_at  = timezone.now() +timedelta(minutes=100)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'token for {self.user.username}'