from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blog.utils.searchengine import SearchEngine
from django.db.models import Q
from blog.models import Post
from blog.serializers.search_serializer import PostSearchSerializer

class SearchView(APIView):

    se = SearchEngine()

    def get(self,request):
        query = request.query_params.get('q', '').strip()
        if len(query) <=2 or not query:
            return Response({'error':'the length of the search should be at least 2'}, status=status.HTTP_400_BAD_REQUEST)
        
        posts = Post.objects.filter(is_published=True).select_related('author').distinct()
        self.se.build_index(posts)
        rankings = self.se.search(query)
        post_ids = [post_id for post_id,score in rankings]

        posts = Post.objects.filter(id__in=post_ids, is_published=True).select_related('author')

        post_dict= {post.id:post for post in posts }
        ordered_posts = [post_dict[pid] for pid in post_ids if pid in post_dict ]

        serializer = PostSearchSerializer(ordered_posts, many=True)

        return Response({
            'query':query,
            'count':len(posts),
            'results':serializer.data
        })