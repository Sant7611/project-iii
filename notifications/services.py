from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notifications.models import Notification


class NotificationService:


    @staticmethod
    def send_notification(
        user,
        event
    ):

        notification = Notification.objects.create(
            recipient=user,
            title=event['title'],
            body=event['body'],
            notification_type=event['notification_type']
        )


        channel_layer = get_channel_layer()


        async_to_sync(
            channel_layer.group_send
        )(
            f"notification_{user.id}",
            {
                "type": "send_notification",
                "id": notification.id,
                "title": notification.title,
                "body": notification.body,
                "created_at": str(notification.created_at),
                "notification_type": notification.notification_type
            }
        )


        return notification