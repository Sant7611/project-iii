from rest_framework import serializers
from blog.models import Comment


class CommentListSerializer(serializers.ModelSerializer):
    reply_count = serializers.IntegerField(source='replies.count' ,read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields=('id',  'author', 'parent', 'content','created_at', 'reply_count')
        read_only_fields = ('id', 'author', 'created_at', 'reply_count')


class CommentDetailSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields=('id', 'author', 'parent', 'content', 'created_at','replies')
        read_only_fields = ('id', 'author', 'created_at', 'replies')

    def get_replies(self,obj):
        if obj.replies.exists():
            serializer = CommentListSerializer(obj.replies.all(), many=True)
            return serializer.data
        return []