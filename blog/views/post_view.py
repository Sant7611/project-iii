from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAuthenticated)
from ..permissions import IsOwnerorReadOnly
from rest_framework.decorators import action
from ..models import  Post
from rest_framework import viewsets
from ..paginations import PageNumPagination
from blog.serializers.post_serializer import PostSerializer, PostCreateUpdateSerializer
from django.utils import timezone
from rest_framework.response import Response
from blog.utils.filters import PostFilter


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('tags', 'comments', 'categories')
    serializer_class  = PostSerializer
    pagination_class = PageNumPagination
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerorReadOnly]
    filterset_class = PostFilter

    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.filter(is_published=True)
            return queryset
        return self.queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer
    
    @action(detail=False, methods=['get'], url_path='my-posts', permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        posts = self.queryset.filter(author=request.user).order_by('-created_at')

        page = self.paginate_queryset(posts)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        post.is_published=True
        post.updated_at=timezone.now()
        post.save(update_fields=['is_published', 'updated_at'])

        serializer = self.get_serializer(post)
        return Response({
            'message':'post published successfully',
            'post':serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        post = self.get_object()
        post.is_published=False
        post.updated_at=timezone.now()
        post.save(update_fields=['is_published', 'updated_at']  )

        serializer = self.get_serializer(post)
        return Response({
            'message':'post unpublished successfully',
            'post':serializer.data
        })