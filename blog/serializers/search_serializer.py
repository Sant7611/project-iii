from rest_framework import serializers


class PostSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    excerpt = serializers.SerializerMethodField()
    author = serializers.IntegerField(source="author.id", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    author_avatar = serializers.SerializerMethodField()
    featured_img = serializers.ImageField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_excerpt(self, obj):
        content = obj.content or ""
        return content[:100] if len(content) >= 100 else content

    def get_author_avatar(self, obj):
        profile = getattr(obj.author, "profile", None)
        avatar = getattr(profile, "avatar", None)
        return avatar.url if avatar else None
