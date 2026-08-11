from django.db.models.aggregates import Count
from rest_framework import generics
from utils.response_helper import success_response,error_response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny

User = get_user_model()
class AdminDashboardView(generics.GenericAPIView):
    
    permission_classes = [AllowAny]  
    
    def get(self, request, *args, **kwargs):
        try:
            
            overview = User.objects.aggregate(
                total_users=Count('id', filter=Q())
            )

        except Exception as e:
            return error_response(message=str(e))