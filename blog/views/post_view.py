from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated)
from ..permissions import IsOwnerorReadOnly, IsCommentAuthorOrPostOwnerOrStaff, ReadOnly
from rest_framework.decorators import action
from ..models import  Post
from rest_framework import viewsets
from ..paginations import PageNumPagination
from blog.serializers.post_serializer import PostSerializer, PostCreateUpdateSerializer
from time import timezone


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('tags', 'comments')
    serializer_class  = PostSerializer
    pagination_class = PageNumPagination
    permission_classes = [IsOwnerorReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            queryset = Post.objects.filter(is_published=True)
            return queryset
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer
    
    @action(detail=True, methods=['post'], url_name='my-posts', permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        queryset = Post.objects.filter(author=request.user).order_by('-created_at')
        serializer = PostSerializer(queryset, many=True)
        return serializer.data
    
    @action(detail=True, methods=['post'])
    def publish(self, request):
        post = self.get_object()
        post.is_published=True
        post.published_at=timezone.now()
        post.save()

        serializer = PostSerializer(post, context=self.get_serializer_context())
        return Response({
            'message':'post published successfully',
            'post':serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request):
        post = self.get_object()
        post.is_published=False
        post.published_at=None
        post.save()

        serializer = PostSerializer(post, context=self.get_serializer_context())
        return Response({
            'message':'post unpublished successfully',
            'post':serializer.data
        })
    