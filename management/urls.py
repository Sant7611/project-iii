# management/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from management.views.user_management import UserManagementViewSet

router = DefaultRouter()

router.register(
    r"management/users",
    UserManagementViewSet,
    basename="management-user",
)

urlpatterns = [
    path("", include(router.urls)),
]
