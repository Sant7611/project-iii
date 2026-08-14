from rest_framework.permissions import  IsAuthenticated
from utils.permissions import IsOwnerOrReadOnly, IsModeratorOrSuperAdmin
from rest_framework.decorators import action
from blog.models import  Post
from rest_framework import viewsets
from blog.serializers.post_serializer import PostSerializer, PostCreateUpdateSerializer, PostModerationSerializer, OwnerPostListSerializer, OwnerPostSerializer
from blog.utils.filters import PublicPostFilter, MyPostFilter
from utils.response_helper import success_response, error_response
from notifications.services import NotificationService
from django.utils import timezone
from notifications.models import Notification
from django.db.models import Q
from rest_framework.response import Response


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('tags', 'comments', 'categories')
    serializer_class  = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filterset_class = PublicPostFilter
    ordering_fields= ['title', 'created_at']
    ordering =['-created_at']

    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if self.action == "my_posts":
            return queryset.filter(author=user)

        if (
            user.is_authenticated
            and user.role in ["moderator", "super_admin"]
        ):
            return queryset

        if self.action == "retrieve" and user.is_authenticated:
            return queryset.filter(
                Q(approval_status=Post.PostStatus.APPROVED) | Q(author=user)
            )

        if self.action in ["update", "partial_update", "destroy"]:
            return queryset.filter(author=user)

        return queryset.filter(
            approval_status=Post.PostStatus.APPROVED
        )
    

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer

        if self.action == "my_posts":
            return OwnerPostListSerializer

        if self.action in ["accept", "reject"]:
            return PostModerationSerializer

        user = self.request.user
        if (
            user.is_authenticated
            and user.role in ["moderator", "super_admin"]
        ):
            return PostModerationSerializer

        return PostSerializer

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()

        if (
            request.user.is_authenticated
            and request.user.role in ["moderator", "super_admin"]
        ):
            serializer = self.get_serializer(post)
        elif post.author_id == request.user.id:
            serializer = OwnerPostSerializer(post, context=self.get_serializer_context())
        else:
            serializer = self.get_serializer(post)

        return Response(serializer.data)

    def perform_update(self, serializer):
        should_resubmit = (
            serializer.instance.author_id == self.request.user.id
            and serializer.instance.approval_status != Post.PostStatus.PENDING
        )
        post = serializer.save()

        if should_resubmit:
            post.approval_status = Post.PostStatus.PENDING
            post.reviewed_by = None
            post.reviewed_at = None
            post.rejection_reason = ""
            post.save(
                update_fields=[
                    "approval_status",
                    "reviewed_by",
                    "reviewed_at",
                    "rejection_reason",
                ]
            )
    
    @action(detail=False, methods=['get'], url_path='my-posts', permission_classes=[IsAuthenticated], filterset_class=MyPostFilter)
    def my_posts(self, request):

        posts = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return success_response(data=serializer.data, status=200)
    
    
    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrSuperAdmin])
    def accept(self, request, pk=None):
        post = self.get_object()
        if post.approval_status == Post.PostStatus.APPROVED:
            return error_response(message='post already approved', status=400)
        post.approval_status=Post.PostStatus.APPROVED
        post.reviewed_by = request.user
        post.reviewed_at = timezone.now()
        post.rejection_reason = ""
        post.save(update_fields=['approval_status', 'reviewed_by', 'reviewed_at', 'rejection_reason'])
        
        event = {
             "title":"Post Approval",
             "body":"Your post has been approved",
             "notification_type":(
            Notification.NotificationChoices.POST_APPROVED
        ),
        }
        
        NotificationService.send_notification(user=post.author,event=event )

        serializer = self.get_serializer(post)
        return success_response(data={
            'message':'post approved',
            'post':serializer.data
        }, status=200)
    
    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrSuperAdmin])
    def reject(self, request, pk=None):
        post = self.get_object()
        if post.approval_status == Post.PostStatus.REJECTED:
            return error_response(message='post already rejected', status=400)
        reason = request.data.get("reason", "").strip()
        if not reason:
            return error_response(message='rejection reason is required', status=400)
        post.approval_status=Post.PostStatus.REJECTED
        post.reviewed_by = request.user
        post.reviewed_at = timezone.now()
        post.rejection_reason = reason

        post.save(update_fields=['approval_status', 'reviewed_by', 'rejection_reason', 'reviewed_at'])

        event = {
             "title":"Post Rejected",
             "body":"Your post has been rejected",
             "notification_type":Notification.NotificationChoices.POST_REJECTED
        }

        NotificationService.send_notification(user=post.author,event=event )


        serializer = self.get_serializer(post)
        return success_response(data={
            'message':'post rejected ',
            'post':serializer.data
        }, status=200)
