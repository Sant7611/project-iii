from rest_framework import serializers
from base.serializers import BaseModelSerializer
from notifications.models import Notification

class NotificationSerializer(BaseModelSerializer):
    post = serializers.SerializerMethodField(read_only=True)

    def get_post(self, obj):
        if obj.post:
            return {
                "id": obj.post.id,
                "slug": obj.post.slug
            }
        return None

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "body",
            "post",
            "notification_type",
            "is_read",
            "created_at",
        )
        read_only_fields = (
            "id",
            "title",
            "body",
            "notification_type",
            "created_at",
            "post"
        )
