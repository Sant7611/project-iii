from rest_framework import serializers
from blog.models import Post

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'author_username', 
                  'is_published', 'view_count', 'featured_img', 'short_code', 
                  'created_at', 'updated_at']
        read_only_fields= ('id', 'slug', 'author', 'view_count', 'short_code', 'created_at', 'updated_at')

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields = ['title', 'content', 'tags', 'featured_img']
