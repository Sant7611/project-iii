from rest_framework import generics,status
from django.contrib.auth import get_user_model
from accounts.serializers.register_serializer import RegisterSerializer 
from accounts.models import Profile
from rest_framework.response import Response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer