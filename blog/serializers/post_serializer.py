from rest_framework import serializers
from blog.models import Post, Tag

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'author_username', 
                  'is_published', 'view_count', 'featured_img', 'short_code', 'tags',
                  'created_at', 'updated_at']
        read_only_fields= ('id', 'slug', 'author', 'view_count', 'short_code', 'created_at', 'updated_at')

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='name', queryset=Tag.objects.all())

    class Meta:
        model=Post
        fields = ['title', 'content', 'tags', 'featured_img']

    def create(self, validated_data):
        tags = validated_data.pop('tags',[])
        post = Post.objects.create(**validated_data)

        self._set_tags(post, tags)
        post.save()
        return post

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tags', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tag_names is not None:
            self._set_tags(instance, tag_names)
        
        return instance
    
    def _set_tags(self, post, tags):
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower().strip())
            post.tags.add(tag)