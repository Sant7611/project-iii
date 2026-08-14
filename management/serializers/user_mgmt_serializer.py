from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from accounts.serializers.profile_serializer import ProfileSerializer

User = get_user_model()


class UserManagementSerializer(ModelSerializer):
    profile = ProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ['id', 'profile', 'first_name', 'last_name', 'email', 'username', 'phone', 'role']
        read_only_fields = fields
        
    