from rest_framework.serializers import ModelSerializer
from blog.models import Like


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ('post', 'user')
