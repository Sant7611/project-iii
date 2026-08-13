from rest_framework import generics
from rest_framework.permissions import AllowAny
from utils.response_helper import success_response, error_response
from django.contrib.auth import get_user_model


User = get_user_model()

class ModeratorDashboard(generics.GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            pass
        except Exception as e:
            return e