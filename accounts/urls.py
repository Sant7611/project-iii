from django.urls import include, path
from accounts.views import login_view, register_view, profile_view
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()
routers.register(r'profile', profile_view.ProfileView, basename='profile')

urlpatterns = [
        path('auth/register/',register_view.RegisterView.as_view() , name='register'),
        path('auth/login/', login_view.LoginView.as_view(), name='login'),
        path('', include(routers.urls)),
        
        # path('api/detail/<str:uname>/', , name='details'),
        # path('api/test_decorator/', views.test_decorator, name='test_decorator'),
        # path('api/user_logout/', views.user_logout, name='user_logout')
]
