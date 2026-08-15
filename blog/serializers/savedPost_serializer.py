from rest_framework.serializers import ModelSerializer
from blog.models import SavedPost


class SavedPostSerializer(ModelSerializer):
    class Meta:
        model=SavedPost
        fields = ["post"]
        read_only_fileds = ('user',)