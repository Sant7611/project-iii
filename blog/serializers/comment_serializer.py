from rest_framework import serializers
from blog.models import Comment
from base.serializers import BaseModelSerializer


class CommentListSerializer(BaseModelSerializer):
    reply_count = serializers.IntegerField(source='replies.count' ,read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    class Meta(BaseModelSerializer.Meta):
        model = Comment
        fields=('id',  'author', 'parent', 'content','created_at', 'reply_count')
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ('author', 'reply_count')


class CommentDetailSerializer(BaseModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = CommentListSerializer(many=True, read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Comment
        fields = (
            'id',
            'author',
            'parent',
            'content',
            'created_at',
            'replies',
        )

        read_only_fields = (
            BaseModelSerializer.Meta.read_only_fields
            + ('author', 'replies')
        )