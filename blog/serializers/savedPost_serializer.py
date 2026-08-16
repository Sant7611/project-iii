from rest_framework.serializers import ModelSerializer
from blog.models import SavedPost


class SavedPostSerializer(ModelSerializer):
    class Meta:
        model=SavedPost
        fields = ['id', "post",'user', 'created_at']
        read_only_fields = ('user',)