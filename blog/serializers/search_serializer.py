from rest_framework import serializers


class PostSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    excerpt = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.username", read_only=True)
    created_at = serializers.DateTimeField()

    class Meta:
        fields = ('id', 'title', 'excerpt', 'author', 'created_at')

    
    def get_excerpt(self, obj):
        content = obj.content or ''
        return content[:100] if len(content) >=100 else content