from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils import timezone

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        # Every account has one private group. This gives every persisted
        # notification a matching recipient and notification ID.
        self.group_name = f"notification_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'event':'connection',
            'message':'connection successfully established.'
        }))

    async def disconnect(self, close_code):
        
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            
        
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'event':'notification',
            'data':{
                'id':event['id'],
                'title':event['title'],
                "notification_type": event.get("notification_type", "post_pending"),
                "post_id": event.get("post_id", None),
                "slug": event.get("slug", None),
                "created_at": event.get("created_at", timezone.now()),
                "is_read": event.get("is_read", False),
                'body':event['body']
            }
        }))
