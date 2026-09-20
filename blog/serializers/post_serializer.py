from django.core.files.storage import default_storage
from rest_framework import serializers
from blog.models import Post, Tag
from base.serializers import BaseModelSerializer

class PostSerializer(BaseModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True, read_only=True)

    def get_author_avatar(self, obj):
        profile = getattr(obj.author, 'profile', None)
        avatar = getattr(profile, 'avatar', None)
        return avatar.url if avatar else None
    class Meta(BaseModelSerializer.Meta):
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'author', 'author_username', 'author_avatar', 'view_count', 'featured_img', 'short_code', 'tags',
                  'created_at', 'updated_at']
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ('slug', 'author', 'view_count', 'short_code')

class PostCreateUpdateSerializer(BaseModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    clear_featured_img = serializers.BooleanField(required=False, write_only=True, default=False)
    
    class Meta(BaseModelSerializer.Meta):
        model=Post
        fields = ['id','title', 'content', 'tags', 'featured_img', 'clear_featured_img']

    def create(self, validated_data):
        tags = validated_data.pop('tags', None)
        validated_data.pop('clear_featured_img', None)

        post = super().create(validated_data)

        if tags is not None:
            self._set_tags(post, tags)

        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        clear_featured_img = validated_data.pop('clear_featured_img', False)
        replacing_image = 'featured_img' in validated_data
        old_image_name = instance.featured_img.name if instance.featured_img else ''

        if clear_featured_img:
            validated_data['featured_img'] = None

        post = super().update(instance, validated_data)

        if old_image_name and (clear_featured_img or replacing_image):
            try:
                default_storage.delete(old_image_name)
            except Exception:
                pass
        
        if tags is not None:
            self._set_tags(post, tags)
        
        return post
    
    def _set_tags(self, post, tags):
        taglist=[]
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower().strip())
            taglist.append(tag)
        post.tags.set(taglist)
        
    def to_representation(self, instance):
        return PostSerializer(
            instance,
            context=self.context,
        ).data
        
class OwnerPostListSerializer(PostSerializer):
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            "approval_status",
            "reviewed_at",
        ]
        read_only_fields = PostSerializer.Meta.read_only_fields + (
            "approval_status",
            "reviewed_at",
        )


class OwnerPostSerializer(OwnerPostListSerializer):
    class Meta(OwnerPostListSerializer.Meta):
        fields = OwnerPostListSerializer.Meta.fields + ["rejection_reason"]
        read_only_fields = OwnerPostListSerializer.Meta.read_only_fields + (
            "rejection_reason",
        )

class PostModerationSerializer(OwnerPostSerializer):
    reviewed_by_username = serializers.CharField(
        source="reviewed_by.username",
        read_only=True,
        allow_null=True,
    )

    class Meta(OwnerPostSerializer.Meta):
        fields = OwnerPostSerializer.Meta.fields + [
            "reviewed_by",
            "reviewed_by_username",
        ]
        read_only_fields = OwnerPostSerializer.Meta.read_only_fields + (
            "reviewed_by",
            "reviewed_by_username",
        )


