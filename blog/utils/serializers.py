from rest_framework import serializers
from blog.models import Post, Comment
from django.shortcuts import get_object_or_404

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