from django.urls import path
from accounts.views import login_view, register_view, profile_view

urlpatterns = [
        path('auth/register/',register_view.RegisterView.as_view() , name='register'),
        path('auth/login/', login_view.LoginView.as_view(), name='login'),
        path('profile/me/', profile_view.ProfileView.as_view(), name='my-profile'),
        
        # path('api/detail/<str:uname>/', , name='details'),
        # path('api/test_decorator/', views.test_decorator, name='test_decorator'),
        # path('api/user_logout/', views.user_logout, name='user_logout')
]
