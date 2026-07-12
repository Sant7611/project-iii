from django.urls import path, include
from blog.views import post_view, refresh_token
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView
from blog.views.search_view import SearchView



router = DefaultRouter()
router.register(r'posts', post_view.PostView, basename='post')

# router.register(r'comments', views.CommentViewset, basename='comment')

# post_comment_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
# post_comment_router.register(r'comments', views.CommentViewset, basename='post-comments')

urlpatterns = [
    path('api/',include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('api/search/', SearchView.as_view(), name='search'),
    # path('api/', include(post_comment_router.urls))


    # path('api/posts/<int:pk>/',views.ListView.as_view()),
    
    # path('api/posts/<int:pk>/', views.post_detail, name='post_details'),
    # path('api/posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    # path('api/comments/<int:pk>/', views.comment_detail, name='comment_detail'),
    # path('api/search/', views.search, name='search'), 
    # path('api/posts/<int:post_id>/like/', views.like, name='like'),
    # path('api/posts/recommend/<int:user_id>/', views.recommender, name='recommender')
]
