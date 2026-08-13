from accounts.models import Profile, User
from rest_framework import serializers
from base.serializers import BaseModelSerializer


class ProfileSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Profile
        fields = ['bio', 'avatar', 'address']
        
        
class UserSerializer(BaseModelSerializer):
    profile = ProfileSerializer()
    class Meta(BaseModelSerializer.Meta):
        model = User
        fields = ['id', 'profile', 'first_name', 'last_name', 'email', 'username', 'phone']
        
    def update(self,instance, validated_data):
        profile_data = validated_data.pop('profile')
        instance = super().update(instance, validated_data)
        
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance