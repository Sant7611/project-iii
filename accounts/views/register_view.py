from rest_framework import generics
from django.contrib.auth import get_user_model
from accounts.serializers.register_serializer import RegisterSerializer 

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []
