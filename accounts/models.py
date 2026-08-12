from django.db import models
from django.contrib.auth.models import AbstractUser
from base.models import BaseModel
class User(AbstractUser, BaseModel):
    
    ROLE_CHOICES=(
        ('super_admin', 'Super Admin'),
        ('moderator', 'Moderator'),
        ('user', 'user')
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=50, default='user', choices=ROLE_CHOICES)
    is_deleted=models.BooleanField(default=False)
    email=models.EmailField(unique=True)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']
    class Meta:
        constraints= [
            models.UniqueConstraint(
                fields=['username'],
                condition=models.Q(is_deleted=False, is_active=True),
                name="unique_username_for_active_users"
            ),
            models.UniqueConstraint(
                fields=['phone'],
                condition=models.Q(is_deleted=False, is_active=True) & ~models.Q(phone=''),
                name="unique_phone_for_active_users"
            )
        ]

    # AbstractUser already has: username, password, email, first_name, last_name,
    # is_staff, is_active, is_superuser, date_joined, last_login
    # So we DON'T redefine them. We only add what's extra.
    
    def __str__(self):
        return self.username


class Profile(models.Model):
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    address = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"{self.user.username}"