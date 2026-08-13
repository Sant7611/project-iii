from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAuthenticated)
from blog.permissions import IsOwnerorReadOnly, IsAdminOrModerator
from rest_framework.decorators import action
from blog.models import  Post
from rest_framework import viewsets
from blog.serializers.post_serializer import PostSerializer, PostCreateUpdateSerializer, PostModerationSerializer, OwnerPostSerializer
from blog.utils.filters import PostFilter
from utils.response_helper import success_response, error_response
from notifications.services import NotificationService
from django.utils import timezone


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('tags', 'comments', 'categories')
    serializer_class  = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerorReadOnly]
    filterset_class = PostFilter
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

        if self.action in ["update", "partial_update", "destroy"]:
            return queryset.filter(author=user)

        return queryset.filter(
            approval_status=Post.PostStatus.APPROVED
        )
    

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer

        if self.action == "my_posts":
            return OwnerPostSerializer

        if self.action in ["accept", "reject"]:
            return PostModerationSerializer

        user = self.request.user
        if (
            user.is_authenticated
            and user.role in ["moderator", "super_admin"]
        ):
            return PostModerationSerializer

        return PostSerializer
    
    @action(detail=False, methods=['get'], url_path='my-posts', permission_classes=[IsAuthenticated])
    def my_posts(self, request):

        posts = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return success_response(data=serializer.data, status=200)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrModerator])
    def accept(self, request, pk=None):
        post = self.get_object()
        if post.approval_status == PostStatus.APPROVED:
            return error_response(data={'message':'post already approved'}, status=400)
        post.approval_status=Post.PostStatus.APPROVED
        post.reviewed_by = request.user
        post.reviewed_at = timezone.now()
        post.save(update_fields=['approval_status', 'reviewed_by', 'reviewed_at'])
        
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrModerator])
    def reject(self, request, pk=None):
        post = self.get_object()
        if post.approval_status == PostStatus.REJECTED:
            return error_response(data={'message':'post already rejected'}, status=400)
        post.approval_status=Post.PostStatus.REJECTED
        post.reviewed_by = request.user
        post.reviewed_at = timezone.now()
        post.rejection_reason = request.data.get("reason", "").strip()
        
        if not post.rejection_reason:
            return error_response(data={'message':'rejection reason is required'}, status=400)

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