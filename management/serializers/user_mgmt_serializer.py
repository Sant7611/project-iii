from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.serializers.profile_serializer import ProfileSerializer
from accounts.serializers.register_serializer import RegisterSerializer

User = get_user_model()


class UserManagementSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ['id', 'profile', 'first_name', 'last_name', 'email', 'username', 'phone', 'role']
        read_only_fields = fields
        
class ModeratorRegisterSerializer(RegisterSerializer):
    class Meta(RegisterSerializer.Meta):
        model = User
        fields = RegisterSerializer.Meta.fields + ('role','phone',)
        
    def create(self, validated_data):
        user = super().create(validated_data)
        user.role = "moderator"
        user.save(update_fields=["role"])
        return user
        
    def validate(self, attrs):
        attrs = super().validate(attrs)

        request = self.context["request"]
        if request.user.role != "super_admin":
            raise serializers.ValidationError(
                "Only a super-admin can create moderators."
            )

        return attrs
    
    def to_representation(self, instance):
        data = {
            "id":instance.id,
            "username":instance.username,
            "email":instance.email,
            "role":instance.role
        }
        return data