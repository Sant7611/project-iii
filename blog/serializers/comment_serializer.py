from rest_framework import serializers
from blog.models import Comment


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