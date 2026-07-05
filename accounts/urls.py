from django.urls import path
from . import views

urlpatterns = [
        path('api/register/', views.register, name='register'),
        path('api/detail/<str:uname>/', views.register, name='details'),
        path('api/test_decorator/', views.test_decorator, name='test_decorator'),
        path('api/user_logout/', views.user_logout, name='user_logout')
]
