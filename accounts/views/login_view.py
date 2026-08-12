from rest_framework import generics
from accounts.serializers.login_serilaizer import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from utils.response_helper import success_response, error_response

class LoginView(generics.GenericAPIView):
    
    
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
        return success_response(data=data, status=200)