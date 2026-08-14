from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from management.serializers.user_mgmt_serializer import UserManagementSerializer 


User = get_user_model()


class PostManagementSerializer(ModelSerializer):
    user = UserManagementSerializer(required=False, many=True)
    class Meta:
        model = User
        fields = ['id', 'profile', 'first_name', 'last_name', 'email', 'username', 'phone']
        read_only_fields = fields