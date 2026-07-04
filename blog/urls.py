from django.urls import path
from . import views


urlpatterns = [
    path('api/posts/',views.home, name='home'),
    path('api/posts/<int:pk>/', views.post_detail, name='post_details'),
    path('api/posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('api/comments/<int:pk>/', views.comment_detail, name='comment_detail'),
    path('api/search/', views.search, name='search'), 
    path('api/posts/<int:post_id>/like/', views.like, name='like'),
    path('api/posts/recommend/<int:user_id>/', views.recommender, name='recommender')
]
