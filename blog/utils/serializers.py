from rest_framework import serializers
from blog.models import Post, Comment
from django.shortcuts import get_object_or_404

# def post_to_dict(post):
#     """Convert a Post model to a JSON-serializable dictionary."""
#     return {
#         "id": post.id,
#         "title": post.title,
#         "slug": post.slug,
#         "short_code": post.short_code,
#         "content": post.content,
#         "author": {
#             "id": post.author.id,
#             "username": post.author.username,
#         },
#         "is_published": post.is_published,
#         "view_count": post.view_count,
#         "featured_img": post.featured_img.url if post.featured_img else None,
#         "tags": [tag.name for tag in post.tags.all()],
#         "created_at": post.created_at.isoformat(),
#         "updated_at": post.updated_at.isoformat(),
#     }

# def comment_to_dict(comment):
#     return {
#         'id': comment.id,
#         'author': comment.author.username,
#         'content': comment.content,
#         'created_at': comment.created_at.isoformat(),
#         'replies': [comment_to_dict(reply) for reply in comment.replies.all()],
#     }


#upgrading to model serializer.
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'author_username', 
                  'is_published', 'view_count', 'featured_img', 'short_code', 
                  'created_at', 'updated_at']

class CommentListSerializer(serializers.ModelSerializer):
    reply_count = serializers.IntegerField(source='replies.count' ,read_only=True)
    class Meta:
        model = Comment
        fields=('id', 'post', 'author', 'parent', 'content','created_at', 'reply_count')
        read_only_fields = ('id', 'created_at', 'reply_count', 'author')


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields=('id', 'post', 'author', 'parent', 'content', 'replies')

    def get_replies(self,obj):
        serializer = CommentListSerializer(obj.replies.all(), many=True)
        return serializer.data