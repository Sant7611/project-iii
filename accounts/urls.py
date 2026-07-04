from django.urls import path
from . import views

urlpatterns = [
        path('api/register/', views.register, name='register'),
        path('api/detail/<str:uname>', views.register, name='register')
]
