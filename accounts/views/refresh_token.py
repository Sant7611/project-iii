from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView
from rest_framework import status
from utils.response_helper import success_response, error_response

class RefreshView(GenericAPIView):
    def post(self, request):
        token = request.data.get('refresh')
        if not token:
            # return Response({'error':'refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            return error_response(message='refresh token is required', status=status.HTTP_400_BAD_REQUEST)
        try:

            refresh = RefreshToken(token)
            return success_response(data={'access':refresh.access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(errors=str(e), status=status.HTTP_401_UNAUTHORIZED)