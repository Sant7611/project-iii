from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from blog.permissions import IsOwnerorReadOnly, IsCommentAuthorOrPostOwnerOrStaff
from blog.models import Comment
from blog.serializers.comment_serializer import CommentDetailSerializer, CommentListSerializer

class Comment_View(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('post', 'author','parent').prefetch_related('replies')
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthorOrPostOwnerOrStaff ]

    def get_serializer_class(self):
        if self.action == 'list':
            return CommentListSerializer
        return CommentDetailSerializer
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id is not None:
            queryset = self.queryset.filter(post_id=post_id)
            if self.action == 'list':
                return queryset.filter(parent=None)
            return queryset
        return self.queryset
    
    def perform_create(self, serializer):
            serializer.save(
                author = self.request.user,
                post_id = self.kwargs.get('post_pk')
            )
        