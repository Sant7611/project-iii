from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from utils.response_helper import success_response, error_response
from rest_framework import status

class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.data.get('refresh')
            if refresh:
                token = RefreshToken(refresh)
                token.blacklist()
                return success_response(message='user successfully logged out', status_code=status.HTTP_200_OK)
            return error_response(message='refresh token is required', status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(errors=str(e), status_code=status.HTTP_400_BAD_REQUEST)