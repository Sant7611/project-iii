from rest_framework import viewsets, mixins
from django.contrib.auth import get_user_model
from management.serializers.user_mgmt_serializer import UserManagementSerializer
from utils.permissions import CanManageUser
from django.db.models import Count
from blog.serializers.post_serializer import OwnerPostSerializer
from utils.response_helper import success_response

User = get_user_model()


class UserManagementViewSet(mixins.DestroyModelMixin, viewsets.ReadOnlyModelViewSet):

    permission_classes = [CanManageUser]
    serializer_class = UserManagementSerializer

    def get_queryset(self):
        queryset = User.objects.prefetch_related("profile").annotate(
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

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        posts = user.posts.all()
        
        datas = {
            "user": self.get_serializer(user),
            "posts": OwnerPostSerializer(
                data=posts, many=True, context=self.get_serializer_context()
            ).data,
        }

        return success_response(data=datas, status=200)
