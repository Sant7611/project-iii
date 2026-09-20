from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from blog.models import Like, Post
from blog.serializers.like_serializer import LikeSerializer
from utils.response_helper import success_response


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post(self, post_id):
        return get_object_or_404(
            Post,
            id=post_id,
            approval_status=Post.PostStatus.APPROVED,
        )

    def get(self, request, post_id):
        post = self.get_post(post_id)
        like = Like.objects.filter(user=request.user, post=post).first()

        data = {
            'liked': like is not None,
            'count': post.likes.count(),
        }

        if like:
            data['like'] = LikeSerializer(like).data

        return success_response(data=data, status=200)

    def post(self, request, post_id):
        post = self.get_post(post_id)

        like, created = Like.objects.get_or_create(
            user=request.user,
            post=post,
        )

        if not created:
            like.delete()
            return success_response(
                message='post unliked',
                data={
                    'liked': False,
                    'count': post.likes.count(),
                },
                status=200,
            )

        return success_response(
            message='post liked',
            data={
                'liked': True,
                'count': post.likes.count(),
                'like': LikeSerializer(like).data,
            },
            status=201,
        )
