from django.db import models
from base.models import BaseModel
from django.conf import settings

from blog.models import Post

class Notification(BaseModel):
    class NotificationChoices(models.TextChoices):
        POST_PENDING = "post_pending", "Post Pending"
        POST_APPROVED = "post_approved", "Post Approved"
        POST_REJECTED = "post_rejected", "Post Rejected"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    body = models.TextField()
    notification_type = models.CharField(choices=NotificationChoices.choices, max_length=100, default=NotificationChoices.POST_PENDING)
    is_read = models.BooleanField(default=False)
    post= models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient}"
