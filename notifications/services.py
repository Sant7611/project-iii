from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from notifications.models import Notification



class NotificationService:

    @staticmethod
    def send_notification(user, event):

        notification = Notification.objects.create(
            recipient=user,
            title=event["title"],
            body=event["body"],
            notification_type=event["notification_type"],
            post=event.get("post", None),
        )

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"notification_{user.id}",
            {
                "type": "send_notification",
                "id": notification.id,
                "title": notification.title,
                "body": notification.body,
                "post_id": notification.post_id if notification.post else None,
                "slug": notification.post.slug if notification.post else None, 
                "created_at": str(notification.created_at),
                "notification_type": notification.notification_type,
            },
        )

        return notification

    @staticmethod
    def send_to_reviewers(event):
        User = get_user_model()
        
        reviewers = User.objects.filter(
            role__in=["moderator", "super_admin"],
            is_deleted=False,
        )

        channel_layer = get_channel_layer()
       
        for reviewer in reviewers:
            notification =Notification.objects.create(
                recipient=reviewer,
                title=event["title"],
                body=event["body"],
                notification_type=event["notification_type"],
            )


            async_to_sync(channel_layer.group_send)(
                f"notification_{reviewer.id}",
                {
                    "type": "send_notification",
                    "id": notification.id,
                    "title": notification.title,
                    "body": notification.body,
                    "created_at": str(notification.created_at),
                    "notification_type": notification.notification_type,
                },
            )