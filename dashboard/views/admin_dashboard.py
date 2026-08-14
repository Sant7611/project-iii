from django.db.models import Q, aggregates
from rest_framework import generics
from blog.models import Post
from utils.response_helper import success_response, error_response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser
from utils.permissions import IsModeratorOrSuperAdmin

User = get_user_model()


class AdminDashboardView(generics.GenericAPIView):

    permission_classes = [IsModeratorOrSuperAdmin]

    def get(self, request):
        try:

            user_stats = User.objects.aggregate(
                total_users=aggregates.Count(
                    "id", filter=Q(is_active=True, role="user", is_deleted=False)
                )
            )
            
            if request.user.role == 'super_admin':
                user_stats += User.objects.aggregate(
                total_moderators=aggregates.Count(
                    "id", filter=Q(role="moderator", is_active=True, is_deleted=False)
                ))

            post_stats = Post.objects.aggregate(
                total_posts=aggregates.Count("id")
                ,
                approved_posts=aggregates.Count(
                    "id", filter=Q(approval_status="approved")
                ),
                pending_posts=aggregates.Count(
                    "id", filter=Q(approval_status="pending")
                ),
            )

            data = {"user_stats": user_stats, "post_stats": post_stats}

            return success_response(data=data, status=200)

        except Exception as e:
            return error_response(message=str(e))
