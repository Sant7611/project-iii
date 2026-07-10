from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.serializers.login_serilaizer import LoginSerializer

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer