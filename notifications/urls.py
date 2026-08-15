from django.urls import path, include
from notifications.views import NotificationViewSet
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register(r'notification', NotificationViewSet, basename='notifications')
urlpatterns = [
    path('', include(routers.urls))
]
