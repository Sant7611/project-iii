from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required=True)
    password2 = serializers.CharField(write_only = True, required=True)
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs.pop(password2)
        if password != password2:
            raise serializers.ValidationError("Password must match")
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def to_representation(self, instance):
        return {
            'id':instance.id,
            'username':instance.username,
            'email':instance.email,
            'message':'User registered successfully.',
        }