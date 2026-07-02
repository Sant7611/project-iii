from django.urls import path
from . import views


urlpatterns = [
    path('api/posts/',views.home, name='home'),
    path('api/posts/<int:pk>/', views.post_detail, name='post_details')
]
