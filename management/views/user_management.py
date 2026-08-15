from rest_framework import viewsets
from django.contrib.auth import get_user_model
from management.serializers.user_mgmt_serializer import (
    UserManagementSerializer,
    ModeratorRegisterSerializer,
)
from utils.permissions import CanManageUser, IsSuperAdmin
from django.db.models import Count
from blog.serializers.post_serializer import PostModerationSerializer
from utils.response_helper import success_response
from rest_framework.decorators import action

User = get_user_model()


class UserManagementViewSet(viewsets.ModelViewSet):

    permission_classes = [CanManageUser]
    serializer_class = UserManagementSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ModeratorRegisterSerializer
        return UserManagementSerializer

    def get_queryset(self):
        queryset = User.objects.select_related("profile").annotate(
            user_count=Count("posts", distinct=True)
        )
        actor = self.request.user

        if actor.role == "super_admin":
            return queryset.filter(
                role__in=["user", "moderator"], is_deleted=False
            ).exclude(pk=actor.pk)

        if actor.role == "moderator":
            return queryset.filter(role="user", is_deleted=False).exclude(pk=actor.pk)

        return queryset.none()

    @action(detail=False, methods=["post"], permission_classes=[IsSuperAdmin])
    def create_moderator(self, request):
        serializer = ModeratorRegisterSerializer(
            data=request.data,
            context={"request": request},
        )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message='Moderator created successfully', data=serializer.data, status=201)

    def retrieve(self, request, *args, **kwargs):
        managed_user = self.get_object()

        posts = managed_user.posts.select_related(
            "author", "reviewed_by"
        ).prefetch_related("tags")

        data = {
            "user": self.get_serializer(managed_user).data,
            "posts": PostModerationSerializer(
                posts,
                many=True,
                context=self.get_serializer_context(),
            ).data,
        }

        return success_response(data=data, status=200)
