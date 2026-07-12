from blog.serializers.search_serializer import PostSearchSerializer
from rest_framework.views import APIView
from blog.utils.collaborativeRecommender import CollaborativeRecommender
from blog.models import Like, Post
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class Recommendation(APIView):

    permission_classes = [IsAuthenticated]
    cr = CollaborativeRecommender()

    def get(self, request):
        self.cr.build_matrix(Like.objects.all())

        results = self.cr.recommend(request.user.id)
        post_ids = [post_id for post_id, similarity in results]
        posts = Post.objects.filter(id__in=post_ids, is_published=True)
        post_dict = {post.id:post for post in posts}

        ordered_posts = [post_dict[pid] for pid in post_ids if pid in post_dict]
        serializer = PostSearchSerializer(ordered_posts, many=True)

        return Response({
            'count':len(posts),
            'results':serializer.data
        })