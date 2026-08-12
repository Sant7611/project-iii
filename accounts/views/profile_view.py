from rest_framework.viewsets import ModelViewSet
from accounts.models import Profile, User
from accounts.serializers.profile_serializer import UserSerializer


class ProfileView(ModelViewSet):
    queryset= User.objects.all()
    serializer_class= UserSerializer
    
    