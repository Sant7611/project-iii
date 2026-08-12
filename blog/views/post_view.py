from rest_framework.permissions import (IsAuthenticatedOrReadOnly, IsAuthenticated)
from blog.permissions import IsOwnerorReadOnly
from rest_framework.decorators import action
from blog.models import  Post
from rest_framework import viewsets
from blog.serializers.post_serializer import PostSerializer, PostCreateUpdateSerializer
from blog.utils.filters import PostFilter
from utils.response_helper import success_response, error_response


class PostView(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').prefetch_related('tags', 'comments', 'categories')
    serializer_class  = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerorReadOnly]
    filterset_class = PostFilter
    ordering_fields= ['title', 'created_at']
    ordering =['-created_at']

    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.filter(is_published=True)
            return queryset
        return self.queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer
    
    @action(detail=False, methods=['get'], url_path='my-posts', permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        posts = self.filter_queryset(posts)
        
        page = self.paginate_queryset(posts)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return success_response(data=serializer.data, status=200)
    
    # @action(detail=True, methods=['post'])
    # def publish(self, request, pk=None):
    #     post = self.get_object()
    #     post.is_published=True
    #     post.save(update_fields=['is_published'])

    #     serializer = self.get_serializer(post)
    #     return success_response(data={
    #         'message':'post published successfully',
    #         'post':serializer.data
    #     }, status=200)
    
    # @action(detail=True, methods=['post'])
    # def unpublish(self, request, pk=None):
    #     post = self.get_object()
    #     post.is_published=False
    #     post.save(update_fields=['is_published']  )

    #     serializer = self.get_serializer(post)
    #     return success_response(data={
    #         'message':'post unpublished successfully',
    #         'post':serializer.data
    #     }, status=200)
    
    @action(detail=True, methods=['post'], url_path='toggle-publish')
    def toggle_publish(self, request, pk=None):
        post = self.get_object()
        post.is_published = not post.is_published
        post.save(update_fields=['is_published'])

        serializer = self.get_serializer(post)
        return success_response(data={
            'message': 'post publish status toggled successfully',
            'post': serializer.data
        }, status=200)