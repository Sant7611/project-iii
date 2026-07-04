from django.shortcuts import render
from django.contrib import messages
from .models import Category, Comment, Post, Like, Tag
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import get_user_model
from .utils.serializers import post_to_dict, comment_to_dict
from django.core.paginator import Paginator
from .utils.searchengine import SearchEngine

User = get_user_model()
user = User.objects.first()

search_engine = SearchEngine()


@csrf_exempt
def home(request):
    if request.method == "GET":
        posts = (
            Post.objects.filter(is_published=True)
            .select_related("author")
            .prefetch_related("tags")
        )
        page_number = request.GET.get('page', 1)

        paginator = Paginator(posts, 2)
        page_obj = paginator.get_page(page_number)

        return JsonResponse(
            {
                "count": posts.count(),
                "num_pages":paginator.num_pages,
                'current_page':page_obj.number,
                "result": [
                    post_to_dict(post)
                    for post in page_obj
                ],
            }
        )

    elif request.method == "POST":
        if not user:
            return JsonResponse({"error": "no user to assign as author"})

        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")

        is_published = data.get("is_published", False)
        if isinstance(is_published, str):
            is_published = is_published.lower() == "true"

        post = Post.objects.create(
            title=title, content=content, is_published=is_published, author=user
        )

        tags = data.get("tags", [])
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            post.tags.add(tag)

        return JsonResponse(post_to_dict(post), status=201)
    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def post_detail(request, pk):
    try:
        post = Post.objects.select_related("author").get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Not Found"}, status=404)
    if request.method == "GET":
        return JsonResponse(post_to_dict(post))

    elif request.method == "PUT":
        data = json.loads(request.body)
        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        # post.featured_img = data.get("featured_img", post.featured_img.url)
        post.save()
        return JsonResponse(post_to_dict(post))

    elif request.method == "DELETE":
        post.delete()
        return JsonResponse({"message": "The post is deleted"}, status=204)

    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def comment_list(request, post_id):

    if request.method == "GET":
        comments = (
            Comment.objects.filter(post_id=post_id)
            .filter(parent=None)
            .select_related("author")
            .prefetch_related("replies")
        )

        return JsonResponse(
            {
                "count": comments.count(),
                "result": [comment_to_dict(comment) for comment in comments],
            },
            status=200,
        )

    elif request.method == "POST":

        data = json.loads(request.body)

        # we checked the post exits or not here
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        # now check if the comment has anything or not.

        content = data.get("content", "").strip()
        if not content:
            return JsonResponse({"error": "content is required"}, status=400)

        parent_id = data.get("parent_id")
        if parent_id:
            try:
                Comment.objects.get(pk=parent_id, post=post)  
            except Comment.DoesNotExist:
                return JsonResponse({"error": "Parent comment not found"}, status=400)

        comment = Comment.objects.create(
            post=post, author=user, content=content, parent_id=parent_id
        )

        return JsonResponse(comment_to_dict(comment), status=201)

    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def comment_detail(request, pk):
    try:
        comment = (
            Comment.objects.select_related("author")
            .prefetch_related("replies")
            .get(pk=pk)
        )
    except Comment.DoesNotExist:
        return JsonResponse({"error": "The comment does not exist"}, status=404)

    if request.method == "GET":
        return JsonResponse(comment_to_dict(comment))

    elif request.method == "DELETE":
        comment.delete()
        return JsonResponse({"message": "deleted successfully"}, status=200)
    return JsonResponse({"error": "method not allowed"}, status=405)


@csrf_exempt
def search(request):

    if request.method !='GET':
        return JsonResponse({'Error':'GET only'}, status=405)
    
    query = request.GET.get('q', '')
    if len(query) <2 :
        return JsonResponse({'error':"there should be more than 2 chars."}, status=400)
    

    if not search_engine.documents:
        search_engine.build_index(Post.objects.filter(is_published=True))
    
    results = search_engine.search(query)

    return JsonResponse(
        {
            "count": len(results),
            "result": [
                post_to_dict(Post.objects.get(pk=doc_id)) for doc_id, score in results
            ],
        },
        status=200,
    )

@csrf_exempt
def like(request, post_id):

    #check if user exists or not.
    if not user:
        return JsonResponse({'error':'no user available'}, status=400)


    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error':'post not found'}, status=404)
    
    if request.method == 'GET':
        liked = Like.objects.filter(user=user, post=post).exists() #check if user liked post or not
        count = Like.objects.filter(post=post).count()
        return JsonResponse({'count':count, 'liked':liked})
    
    elif request.method == 'POST':
        liked, created = Like.objects.get_or_create(post=post, user=user)
        if not created:
            liked.delete()
            return JsonResponse({'liked':False, 'count':Like.objects.filter(post=post).count()})
        
        return JsonResponse({'liked':True, 'count':Like.objects.filter(post=post).count()})
    return JsonResponse({'error':'method not allowed'}, status=405)