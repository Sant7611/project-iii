from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RefreshView(APIView):
    def post(request):
        token = request.data.get('refresh')
        if not token:
            return Response({'error':'refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:

            refresh = RefreshToken(token)
            return Response({'access':refresh.access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_401_UNAUTHORIZED)