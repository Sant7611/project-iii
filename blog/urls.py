from django.urls import path
from . import views


urlpatterns = [
    path('api/posts/',views.home, name='home'),
    path('api/posts/<int:pk>/', views.post_detail, name='post_details'),
    path('api/posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('api/comments/<int:pk>/', views.comment_detail, name='comment_detail'),
]
