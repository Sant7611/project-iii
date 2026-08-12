from channels.generic.websocket import AsyncWebsocketConsumer



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.accept()
        
        
    async def disconnect(self, code):
        return self.disconnect(self)