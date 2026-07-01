# Django Blog System: DRF Foundation + Algorithms
# 12-Day Build Guide (5-6 hrs/day)

> **No Redis, No Celery** — Pure Django + PostgreSQL/SQLite. Redis studied post-project.
> **Comment System:** Adjacency List (parent_id) — most popular, easiest to understand.

---

## Your Selected Features

| # | Feature | Algorithm | Why This Choice |
|---|---------|-----------|-----------------|
| 1 | Short URLs | Base62 Encoding | Collision-free, bijective, interview-friendly |
| 2 | Comment System | Adjacency List + Recursive CTE | Most popular, easy to query, simple recursion |
| 3 | Search | TF-IDF | Classic IR algorithm, ranks by relevance |
| 4 | Recommendations | Collaborative Filtering (Cosine Similarity) | "Readers who liked X also liked Y" |
| 5 | Popular Posts Cache | In-Memory LFU Cache (Python dict) | No Redis needed, demonstrates cache theory |

---

## Algorithm Definitions

### Base62 Encoding
Converts integer ID to short alphanumeric string (0-9, a-z, A-Z). Repeated division by 62, mapping remainders to character indices. Bijective — every integer maps to exactly one string, zero collisions.

**Time:** O(log_62 n) encode, O(length) decode. **Space:** O(1).

### Adjacency List (Comment Threading)
Each comment stores `parent_id` referencing another comment. Tree traversal via recursive CTE (PostgreSQL) or recursive Python function. Most popular approach — used by Reddit, Disqus, WordPress.

**Time:** O(n) to fetch subtree. **Space:** O(depth) recursion stack.

### TF-IDF (Term Frequency-Inverse Document Frequency)
Statistical relevance measure. TF = (word count in doc) / (total words in doc). IDF = log(total docs / docs containing word). Score = TF * IDF. Higher = more distinctive to that document.

**Time:** O(D * V) to build index. **Space:** O(D * V).

### Cosine Similarity (Collaborative Filtering)
Measures angle between two user preference vectors. sim(A,B) = (A dot B) / (||A|| * ||B||). Value -1 to 1. Near 1 = very similar users. Used to recommend items liked by similar users.

**Time:** O(n) per pair. **Space:** O(U * I) for full matrix.

### LFU Cache (Least Frequently Used)
Cache evicts least-frequently-accessed item when full. Each item tracks access count. On eviction, remove minimum count. For popular posts: high-read posts stay cached, low-read evicted.

**Time:** O(1) get/put with hash map + min-heap. **Space:** O(capacity).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x |
| Database | PostgreSQL (recommended) or SQLite |
| Cache | Python in-memory LFU (no Redis) |
| Search | In-memory TF-IDF index (no Elasticsearch) |
| Frontend | Minimal HTML + vanilla JS (API consumption practice) |
| API Style | Pure Django JSON responses (no DRF yet) |

---

## Project Structure

```
blog_project/
├── manage.py
├── blog_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/
│   ├── __init__.py
│   ├── models.py          # Post, Comment, Tag, Like
│   ├── views.py           # ALL JSON views
│   ├── urls.py            # API routes
│   ├── utils/
│   │   ├── base62.py      # Algorithm 1
│   │   ├── search.py      # Algorithm 3 (TF-IDF)
│   │   ├── recommender.py # Algorithm 4 (Collaborative Filtering)
│   │   └── cache.py       # Algorithm 5 (LFU Cache)
│   └── tests.py
├── users/
│   ├── models.py          # Custom User
│   ├── views.py           # Auth JSON endpoints
│   └── urls.py
└── templates/
    └── index.html         # Minimal frontend
```

---

## Day-by-Day Guide

---

## DAY 1: Project Setup + Base62 Algorithm + Post Model

### Study (2 hrs)
- **Base62 Encoding:** Understand why base conversion works. Work through: encode(12345) -> "dnh".
- **Django Models:** Refresh ForeignKey, ManyToManyField, DateTimeField, SlugField.
- **Custom User Model:** Why `AbstractUser` is needed before first migration.

### Build (3-4 hrs)

**Step 1: Project Setup**
```bash
django-admin startproject blog_project
cd blog_project
python manage.py startapp blog
python manage.py startapp users
```

**Step 2: Custom User Model (users/models.py)**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
```

**Step 3: Settings (blog_project/settings.py)**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'blog',
]

AUTH_USER_MODEL = 'users.User'
```

**Step 4: Base62 Algorithm (blog/utils/base62.py)**
```python
BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num):
    if num == 0:
        return BASE62[0]
    result = []
    while num > 0:
        num, rem = divmod(num, 62)
        result.append(BASE62[rem])
    return ''.join(reversed(result))

def decode(s):
    result = 0
    for char in s:
        result = result * 62 + BASE62.index(char)
    return result
```

**Step 5: Post Model (blog/models.py)**
```python
from django.db import models
from django.conf import settings
from .utils.base62 import encode

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.title.lower().replace(' ', '-')[:50]
        super().save(*args, **kwargs)
        if not self.short_code:
            self.short_code = encode(self.id)
            self.save(update_fields=['short_code'])

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name='tags')

    def __str__(self):
        return self.name
```

**Step 6: Migrations + Admin**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Test
- Create post via admin. Verify `short_code` auto-generated.
- Test `encode(1)` -> "1", `encode(61)` -> "Z", `encode(62)` -> "10".
- Verify `decode(encode(99999)) == 99999`.

### DRF Note
Later: `short_code` becomes `HyperlinkedIdentityField` or custom `SlugRelatedField`.

---

## DAY 2: Post CRUD API + Manual Serialization

### Study (2 hrs)
- **JSON API Design:** RESTful conventions, proper status codes.
- **Manual Serialization:** Why `model_to_dict` fails with FKs/M2Ms.
- **CSRF:** Why APIs need exemption, what DRF's `SessionAuthentication` does.

### Build (3-4 hrs)

**Step 1: Manual Serializer (blog/utils/serializers.py)**
```python
from django.forms.models import model_to_dict

def post_to_dict(post, include_content=False):
    data = {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'short_code': post.short_code,
        'short_url': f'/s/{post.short_code}/',
        'author': {
            'id': post.author.id,
            'username': post.author.username,
        },
        'status': post.status,
        'view_count': post.view_count,
        'tags': [tag.name for tag in post.tags.all()],
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
    }
    if include_content:
        data['content'] = post.content
    return data
```

**Step 2: CRUD Views (blog/views.py)**
```python
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import Post, Tag
from .utils.serializers import post_to_dict

@csrf_exempt
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.filter(status='published').select_related('author')
        paginator = Paginator(posts, 10)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        return JsonResponse({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': [post_to_dict(p) for p in page_obj],
        })

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        data = json.loads(request.body)
        post = Post.objects.create(
            title=data['title'],
            content=data['content'],
            author=request.user,
            status=data.get('status', 'draft')
        )

        # Handle tags
        for tag_name in data.get('tags', []):
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            post.tags.add(tag)

        return JsonResponse(post_to_dict(post, include_content=True), status=201)

@csrf_exempt
def post_detail(request, pk):
    try:
        post = Post.objects.select_related('author').get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        post.view_count += 1
        post.save(update_fields=['view_count'])
        return JsonResponse(post_to_dict(post, include_content=True))

    elif request.method == 'PUT':
        if not request.user.is_authenticated or request.user != post.author:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        data = json.loads(request.body)
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.status = data.get('status', post.status)
        post.save()
        return JsonResponse(post_to_dict(post, include_content=True))

    elif request.method == 'DELETE':
        if not request.user.is_authenticated or request.user != post.author:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        post.delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

def short_redirect(request, short_code):
    try:
        post = Post.objects.get(short_code=short_code, status='published')
        post.view_count += 1
        post.save(update_fields=['view_count'])
        return JsonResponse({
            'id': post.id,
            'title': post.title,
            'url': f'/api/posts/{post.id}/'
        })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
```

**Step 3: URLs (blog/urls.py)**
```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/posts/', views.post_list, name='post-list'),
    path('api/posts/<int:pk>/', views.post_detail, name='post-detail'),
    path('s/<str:short_code>/', views.short_redirect, name='short-redirect'),
]
```

### Test
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":"World","tags":["django","api"]}'

curl http://localhost:8000/api/posts/
curl http://localhost:8000/s/1/
```

### DRF Note
Later: All this becomes `PostViewSet(ModelViewSet)` with `serializer_class = PostSerializer`.

---

## DAY 3: Comment System (Adjacency List)

### Study (2 hrs)
- **Adjacency List:** Each node stores `parent_id`. Recursive traversal builds tree.
- **Tree Traversal:** Pre-order (root, children) vs post-order. Comments use pre-order.
- **N+1 Problem:** Why `select_related` on `parent` matters.

### Build (3-4 hrs)

**Step 1: Comment Model (blog/models.py)**
```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
```

**Step 2: Recursive Serializer (blog/utils/serializers.py)**
```python
def comment_to_dict(comment):
    return {
        'id': comment.id,
        'author': {
            'id': comment.author.id,
            'username': comment.author.username,
        },
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'replies': [comment_to_dict(reply) for reply in comment.replies.all()],
    }

def post_detail_with_comments(post):
    data = post_to_dict(post, include_content=True)
    # Get only top-level comments (no parent)
    top_comments = post.comments.filter(parent=None).select_related('author')
    data['comments'] = [comment_to_dict(c) for c in top_comments]
    return data
```

**Step 3: Comment Views (blog/views.py)**
```python
from .models import Comment

@csrf_exempt
def comment_list(request, post_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(post_id=post_id, parent=None)
        return JsonResponse({
            'count': comments.count(),
            'results': [comment_to_dict(c) for c in comments]
        })

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        data = json.loads(request.body)
        comment = Comment.objects.create(
            post_id=post_id,
            author=request.user,
            parent_id=data.get('parent_id'),
            content=data['content']
        )
        return JsonResponse(comment_to_dict(comment), status=201)

@csrf_exempt
def comment_detail(request, pk):
    try:
        comment = Comment.objects.select_related('author').get(pk=pk)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'DELETE':
        if request.user != comment.author and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        comment.delete()
        return JsonResponse({'message': 'Deleted'}, status=204)

    elif request.method == 'PUT':
        if request.user != comment.author:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        data = json.loads(request.body)
        comment.content = data.get('content', comment.content)
        comment.save()
        return JsonResponse(comment_to_dict(comment))
```

**Step 4: Update URLs**
```python
path('api/posts/<int:post_id>/comments/', views.comment_list, name='comment-list'),
path('api/comments/<int:pk>/', views.comment_detail, name='comment-detail'),
```

### Test
```bash
curl -X POST http://localhost:8000/api/posts/1/comments/ \
  -H "Content-Type: application/json" \
  -d '{"content":"Great post!"}'

curl -X POST http://localhost:8000/api/posts/1/comments/ \
  -H "Content-Type: application/json" \
  -d '{"content":"Thanks!","parent_id":1}'
```

### DRF Note
Later: Recursive serialization uses `SerializerMethodField` or `drf-recursive` package.

---

## DAY 4: TF-IDF Search Engine

### Study (2 hrs)
- **TF-IDF Formula:** TF = count / total words. IDF = log(N / df). Score = TF * IDF.
- **Inverted Index:** Word -> list of documents. Enables fast lookup.
- **Cosine Similarity (preview):** How TF-IDF vectors compare for relevance.

### Build (3-4 hrs)

**Step 1: Search Engine (blog/utils/search.py)**
```python
import math
import re
from collections import Counter, defaultdict

class SearchEngine:
    def __init__(self):
        self.documents = {}      # doc_id -> word_count dict
        self.doc_freq = defaultdict(int)  # word -> num docs containing it
        self.total_docs = 0

    def _tokenize(self, text):
        return re.findall(r'[a-z]+', text.lower())

    def add_document(self, doc_id, title, content):
        text = f"{title} {content}"
        words = self._tokenize(text)
        word_counts = Counter(words)

        self.documents[doc_id] = {
            'counts': word_counts,
            'total': len(words),
            'title': title,
        }
        self.total_docs += 1

        for word in word_counts:
            self.doc_freq[word] += 1

    def _tf(self, word, doc_id):
        doc = self.documents[doc_id]
        return doc['counts'].get(word, 0) / doc['total'] if doc['total'] > 0 else 0

    def _idf(self, word):
        df = self.doc_freq.get(word, 0)
        return math.log(self.total_docs / (df + 1)) + 1  # Smoothed IDF

    def _tfidf(self, word, doc_id):
        return self._tf(word, doc_id) * self._idf(word)

    def search(self, query, top_n=10):
        query_words = self._tokenize(query)
        scores = {}

        for doc_id in self.documents:
            score = sum(self._tfidf(word, doc_id) for word in query_words)
            if score > 0:
                scores[doc_id] = score

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

    def build_index(self, posts):
        self.documents.clear()
        self.doc_freq.clear()
        self.total_docs = 0
        for post in posts:
            self.add_document(post.id, post.title, post.content)
```

**Step 2: Search View (blog/views.py)**
```python
from .utils.search import SearchEngine

# Global search engine instance (rebuilt on server restart)
search_engine = SearchEngine()

def search_posts(request):
    query = request.GET.get('q', '')
    if not query or len(query) < 2:
        return JsonResponse({'error': 'Query too short'}, status=400)

    # Rebuild index if empty (in production, rebuild on post save signal)
    if not search_engine.documents:
        search_engine.build_index(Post.objects.filter(status='published'))

    results = search_engine.search(query)

    posts = []
    for doc_id, score in results:
        try:
            post = Post.objects.select_related('author').get(id=doc_id)
            post_data = post_to_dict(post)
            post_data['search_score'] = round(score, 4)
            posts.append(post_data)
        except Post.DoesNotExist:
            continue

    return JsonResponse({
        'query': query,
        'count': len(posts),
        'results': posts,
    })
```

**Step 3: Signal to Rebuild Index (blog/signals.py)**
```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post
from .views import search_engine

@receiver(post_save, sender=Post)
@receiver(post_delete, sender=Post)
def rebuild_search_index(sender, instance, **kwargs):
    if instance.status == 'published':
        search_engine.build_index(Post.objects.filter(status='published'))
```

**Step 4: URL**
```python
path('api/search/', views.search_posts, name='search'),
```

### Test
```bash
curl "http://localhost:8000/api/search/?q=django"
curl "http://localhost:8000/api/search/?q=python tutorial"
```

### DRF Note
Later: Custom `SearchFilter` backend. `SearchVector` for PostgreSQL full-text.

---

## DAY 5: Like System + User-Item Matrix

### Study (2 hrs)
- **Collaborative Filtering:** User-based vs item-based. User-based = find similar users, recommend what they liked.
- **User-Item Matrix:** Rows = users, columns = items, values = interaction (1/0 or rating).
- **Sparse Matrices:** Most users do not interact with most items — efficient storage matters.

### Build (3-4 hrs)

**Step 1: Like Model (blog/models.py)**
```python
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']  # One like per user per post

    def __str__(self):
        return f"{self.user} likes {self.post}"
```

**Step 2: Like Views (blog/views.py)**
```python
from .models import Like

@csrf_exempt
def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(
            user=request.user,
            post_id=post_id
        )
        if not created:
            like.delete()
            return JsonResponse({'liked': False, 'count': Like.objects.filter(post_id=post_id).count()})
        return JsonResponse({'liked': True, 'count': Like.objects.filter(post_id=post_id).count()})

    elif request.method == 'GET':
        liked = Like.objects.filter(user=request.user, post_id=post_id).exists()
        count = Like.objects.filter(post_id=post_id).count()
        return JsonResponse({'liked': liked, 'count': count})
```

**Step 3: Build User-Item Matrix (blog/utils/recommender.py)**
```python
from collections import defaultdict
import math

class CollaborativeRecommender:
    def __init__(self):
        self.user_items = defaultdict(set)   # user_id -> {post_id, post_id, ...}
        self.item_users = defaultdict(set)   # post_id -> {user_id, user_id, ...}

    def build_matrix(self, likes):
        self.user_items.clear()
        self.item_users.clear()

        for like in likes:
            self.user_items[like.user_id].add(like.post_id)
            self.item_users[like.post_id].add(like.user_id)

    def cosine_similarity(self, user1_items, user2_items):
        intersection = len(user1_items & user2_items)
        if not intersection:
            return 0.0
        return intersection / math.sqrt(len(user1_items) * len(user2_items))

    def get_similar_users(self, target_user_id, n=5):
        target_items = self.user_items.get(target_user_id, set())
        if not target_items:
            return []

        similarities = []
        for user_id, items in self.user_items.items():
            if user_id == target_user_id:
                continue
            sim = self.cosine_similarity(target_items, items)
            if sim > 0:
                similarities.append((user_id, sim))

        return sorted(similarities, key=lambda x: x[1], reverse=True)[:n]

    def recommend(self, target_user_id, n=5):
        target_items = self.user_items.get(target_user_id, set())
        similar_users = self.get_similar_users(target_user_id, n=10)

        scores = defaultdict(float)

        for user_id, similarity in similar_users:
            for post_id in self.user_items[user_id]:
                if post_id not in target_items:
                    scores[post_id] += similarity

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]
```

### Test
```bash
curl -X POST http://localhost:8000/api/posts/1/like/ -H "Content-Type: application/json"
curl http://localhost:8000/api/posts/1/like/
```

### DRF Note
Later: `LikeViewSet` with `create`/`destroy` actions. Recommendation as custom `@action`.

---

## DAY 6: Recommendation API + LFU Cache

### Study (2 hrs)
- **LFU Cache:** Least Frequently Used eviction. Each item has access count. Evict minimum.
- **Cache Invalidation:** When to rebuild recommendations (on new like? periodically?).
- **Memory Management:** Python dict + heap for O(1) operations.

### Build (3-4 hrs)

**Step 1: LFU Cache (blog/utils/cache.py)**
```python
import heapq
from collections import defaultdict

class LFUCache:
    def __init__(self, capacity=100):
        self.capacity = capacity
        self.cache = {}           # key -> value
        self.freq = {}            # key -> access count
        self.min_freq = 0
        self.freq_map = defaultdict(set)  # freq -> {key1, key2, ...}

    def get(self, key):
        if key not in self.cache:
            return None

        # Increment frequency
        old_freq = self.freq[key]
        self.freq[key] = old_freq + 1
        self.freq_map[old_freq].discard(key)
        self.freq_map[old_freq + 1].add(key)

        # Update min_freq if needed
        if old_freq == self.min_freq and not self.freq_map[old_freq]:
            self.min_freq += 1

        return self.cache[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.cache:
            self.cache[key] = value
            self.get(key)  # Update frequency
            return

        # Evict if at capacity
        if len(self.cache) >= self.capacity:
            evict_key = min(self.freq_map[self.min_freq], key=lambda k: self.freq[k])
            self.freq_map[self.min_freq].discard(evict_key)
            del self.cache[evict_key]
            del self.freq[evict_key]

        # Insert new
        self.cache[key] = value
        self.freq[key] = 1
        self.freq_map[1].add(key)
        self.min_freq = 1

    def get_stats(self):
        return {
            'size': len(self.cache),
            'capacity': self.capacity,
            'min_freq': self.min_freq,
            'items': {k: self.freq[k] for k in self.cache}
        }
```

**Step 2: Recommendation View (blog/views.py)**
```python
from .utils.recommender import CollaborativeRecommender
from .utils.cache import LFUCache

# Global instances
recommender = CollaborativeRecommender()
rec_cache = LFUCache(capacity=50)  # Cache recommendations per user

def get_recommendations(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    user_id = request.user.id

    # Check cache first
    cached = rec_cache.get(f"rec:{user_id}")
    if cached:
        return JsonResponse({'cached': True, 'results': cached})

    # Build matrix from all likes
    recommender.build_matrix(Like.objects.all())

    # Get recommendations
    recs = recommender.recommend(user_id, n=5)

    # Fetch post details
    results = []
    for post_id, score in recs:
        try:
            post = Post.objects.select_related('author').get(id=post_id)
            post_data = post_to_dict(post)
            post_data['recommendation_score'] = round(score, 4)
            results.append(post_data)
        except Post.DoesNotExist:
            continue

    # Cache result
    rec_cache.put(f"rec:{user_id}", results)

    return JsonResponse({'cached': False, 'results': results})

def get_popular_posts(request):
    cached = rec_cache.get("popular")
    if cached:
        return JsonResponse({'cached': True, 'posts': cached})

    posts = Post.objects.filter(status='published').order_by('-view_count')[:10]
    result = [post_to_dict(p) for p in posts]
    rec_cache.put("popular", result)

    return JsonResponse({'cached': False, 'posts': result})
```

**Step 3: URLs**
```python
path('api/posts/<int:post_id>/like/', views.like_post, name='like-post'),
path('api/recommendations/', views.get_recommendations, name='recommendations'),
path('api/posts/popular/', views.get_popular_posts, name='popular-posts'),
```

### Test
```bash
curl http://localhost:8000/api/recommendations/
curl http://localhost:8000/api/posts/popular/
```

### DRF Note
Later: `@action(detail=False)` on `PostViewSet` for recommendations. Django cache framework replaces LFU.

---

## DAY 7: Authentication + Token System

### Study (2 hrs)
- **Token Authentication:** Why sessions do not work for APIs. Random token vs JWT.
- **Password Hashing:** PBKDF2, why it is slow by design.
- **DRF Auth Flow:** How `TokenAuthentication` header check works.

### Build (3-4 hrs)

**Step 1: Token Model (users/models.py)**
```python
import secrets
import base64
from django.db import models
from django.conf import settings

class APIToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            raw = secrets.token_bytes(32)
            self.key = base64.urlsafe_b64encode(raw).decode().rstrip('=')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token for {self.user}"
```

**Step 2: Auth Views (users/views.py)**
```python
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from .models import APIToken

@csrf_exempt
def login_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    user = authenticate(username=data['username'], password=data['password'])

    if not user:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

    # Deactivate old tokens
    APIToken.objects.filter(user=user).update(is_active=False)

    # Create new token
    token = APIToken.objects.create(user=user)

    return JsonResponse({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })

@csrf_exempt
def register_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if User.objects.filter(username=data['username']).exists():
        return JsonResponse({'error': 'Username taken'}, status=400)

    user = User.objects.create_user(
        username=data['username'],
        email=data.get('email', ''),
        password=data['password']
    )

    token = APIToken.objects.create(user=user)
    return JsonResponse({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
        }
    }, status=201)

def get_user_from_token(request):
    token_key = request.headers.get('X-API-Token')
    if not token_key:
        return None

    try:
        token = APIToken.objects.select_related('user').get(key=token_key, is_active=True)
        return token.user
    except APIToken.DoesNotExist:
        return None
```

**Step 3: Update Views to Use Token (blog/views.py)**
```python
from users.views import get_user_from_token

def post_list(request):
    # Replace request.user with token user
    user = get_user_from_token(request) or request.user
    # ... rest same, use 'user' variable for auth checks
```

### Test
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'

curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'

curl http://localhost:8000/api/posts/ \
  -H "X-API-Token: <token_from_above>"
```

### DRF Note
Later: `rest_framework.authtoken` or `djangorestframework-simplejwt`. Your manual flow becomes `obtain_auth_token`.

---

## DAY 8: Testing All Algorithms

### Study (2 hrs)
- **Unit Testing:** `TestCase`, `Client`, `assertEqual`.
- **Algorithm Testing:** Edge cases, boundary conditions, round-trip verification.
- **API Testing:** Status codes, response structure, auth flows.

### Build (3-4 hrs)

**Step 1: Base62 Tests (blog/tests/test_base62.py)**
```python
from django.test import TestCase
from blog.utils.base62 import encode, decode

class Base62Tests(TestCase):
    def test_encode_zero(self):
        self.assertEqual(encode(0), '0')

    def test_encode_small(self):
        self.assertEqual(encode(61), 'Z')
        self.assertEqual(encode(62), '10')

    def test_roundtrip(self):
        for num in [1, 100, 9999, 1000000]:
            self.assertEqual(decode(encode(num)), num)

    def test_large_number(self):
        large = 999999999999
        self.assertEqual(decode(encode(large)), large)
```

**Step 2: TF-IDF Tests (blog/tests/test_search.py)**
```python
from django.test import TestCase
from blog.utils.search import SearchEngine

class SearchTests(TestCase):
    def setUp(self):
        self.engine = SearchEngine()
        self.engine.add_document(1, "Django Tutorial", "Learn Django framework")
        self.engine.add_document(2, "Flask Guide", "Learn Flask framework")
        self.engine.add_document(3, "Django Advanced", "Advanced Django topics")

    def test_search_django(self):
        results = self.engine.search("django")
        self.assertEqual(len(results), 2)
        # Django Advanced should rank higher (more Django mentions)
        self.assertEqual(results[0][0], 3)

    def test_search_no_results(self):
        results = self.engine.search("ruby")
        self.assertEqual(len(results), 0)

    def test_tfidf_score_positive(self):
        scores = self.engine.search("django")
        for _, score in scores:
            self.assertGreater(score, 0)
```

**Step 3: Recommender Tests (blog/tests/test_recommender.py)**
```python
from django.test import TestCase
from blog.utils.recommender import CollaborativeRecommender

class RecommenderTests(TestCase):
    def setUp(self):
        self.rec = CollaborativeRecommender()
        # Mock likes: user 1 likes posts 1,2,3. user 2 likes 2,3,4. user 3 likes 1
        self.rec.user_items = {
            1: {1, 2, 3},
            2: {2, 3, 4},
            3: {1},
        }
        self.rec.item_users = {
            1: {1, 3},
            2: {1, 2},
            3: {1, 2},
            4: {2},
        }

    def test_similar_users(self):
        similar = self.rec.get_similar_users(1, n=2)
        # User 2 is most similar to user 1 (shares 2,3)
        self.assertEqual(similar[0][0], 2)
        self.assertGreater(similar[0][1], 0)

    def test_recommendations(self):
        recs = self.rec.recommend(3, n=2)
        # User 3 only liked post 1. User 1 (similar) liked 2,3. Should recommend 2 or 3.
        self.assertTrue(len(recs) > 0)
        recommended_ids = [r[0] for r in recs]
        self.assertNotIn(1, recommended_ids)  # Already seen
```

**Step 4: LFU Cache Tests (blog/tests/test_cache.py)**
```python
from django.test import TestCase
from blog.utils.cache import LFUCache

class CacheTests(TestCase):
    def setUp(self):
        self.cache = LFUCache(capacity=3)

    def test_basic_put_get(self):
        self.cache.put("a", 1)
        self.assertEqual(self.cache.get("a"), 1)

    def test_eviction(self):
        self.cache.put("a", 1)
        self.cache.put("b", 2)
        self.cache.put("c", 3)
        self.cache.put("d", 4)  # Should evict "a" (lowest freq)
        self.assertIsNone(self.cache.get("a"))
        self.assertIsNotNone(self.cache.get("b"))

    def test_frequency_tracking(self):
        self.cache.put("a", 1)
        self.cache.get("a")  # freq = 2
        self.cache.get("a")  # freq = 3
        self.cache.put("b", 2)  # freq = 1
        self.cache.put("c", 3)  # freq = 1
        self.cache.put("d", 4)  # Evict b or c (freq 1), not a (freq 3)
        self.assertIsNotNone(self.cache.get("a"))
```

**Step 5: Run Tests**
```bash
python manage.py test blog.tests
```

---

## DAY 9: Refactor to JSON-Only API + DRF Prep

### Study (2 hrs)
- **DRF Serializers:** How `ModelSerializer` auto-generates fields.
- **DRF ViewSets:** How `ModelViewSet` replaces your CRUD views.
- **DRF Routers:** How `DefaultRouter` auto-creates URLs.

### Build (3-4 hrs)

**Step 1: Create DRF-Equivalent Notes (DRF_MIGRATION.md)**

Write a file named DRF_MIGRATION.md with this content:

```markdown
# DRF Migration Guide

## Current (Manual) -> DRF Equivalent

### Serializers

Current: manual dict
```python
post_to_dict(post)
```

DRF: ModelSerializer
```python
class PostSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = StringRelatedField(many=True)
    class Meta:
        model = Post
        fields = '__all__'
```

### Views

Current: function-based
```python
@csrf_exempt
def post_list(request): ...
```

DRF: ViewSet
```python
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

### URLs

Current: manual paths
```python
path('api/posts/', views.post_list)
```

DRF: Router
```python
router = DefaultRouter()
router.register(r'posts', PostViewSet)
```

### Authentication

Current: manual token check
```python
user = get_user_from_token(request)
```

DRF: TokenAuthentication
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}
```

### Pagination

Current: Paginator
```python
paginator = Paginator(posts, 10)
```

DRF: PageNumberPagination
```python
class StandardPagination(PageNumberPagination):
    page_size = 10
```
```

**Step 2: Clean Up Views — Consistent JSON Response Helper**
```python
# blog/utils/response.py
def api_response(data=None, error=None, status=200):
    if error:
        return JsonResponse({'error': error}, status=status)
    return JsonResponse(data, status=status, safe=False)
```

**Step 3: Add API Documentation Endpoint**
```python
def api_docs(request):
    endpoints = {
        'posts': {
            'list': 'GET /api/posts/',
            'create': 'POST /api/posts/',
            'detail': 'GET /api/posts/<id>/',
            'update': 'PUT /api/posts/<id>/',
            'delete': 'DELETE /api/posts/<id>/',
        },
        'comments': {
            'list': 'GET /api/posts/<id>/comments/',
            'create': 'POST /api/posts/<id>/comments/',
        },
        'search': 'GET /api/search/?q=<query>',
        'recommendations': 'GET /api/recommendations/',
        'popular': 'GET /api/posts/popular/',
        'auth': {
            'register': 'POST /api/auth/register/',
            'login': 'POST /api/auth/login/',
        }
    }
    return JsonResponse(endpoints)
```

---

## DAY 10: Frontend + API Consumption

### Study (1.5 hrs)
- **Fetch API:** `fetch()`, promises, async/await.
- **DOM Manipulation:** Creating elements, event listeners.
- **LocalStorage:** Storing auth token client-side.

### Build (3.5-4.5 hrs)

**Minimal Frontend (templates/index.html)**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Blog API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .post { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .tag { background: #f0f0f0; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
        button { padding: 8px 16px; cursor: pointer; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Django Blog API</h1>

    <div id="auth-section">
        <h3>Login</h3>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button onclick="login()">Login</button>
        <p id="auth-status"></p>
    </div>

    <div id="posts-section">
        <h3>Posts</h3>
        <button onclick="loadPosts()">Load Posts</button>
        <div id="posts-list"></div>
    </div>

    <div id="search-section">
        <h3>Search</h3>
        <input type="text" id="search-query" placeholder="Search posts...">
        <button onclick="searchPosts()">Search</button>
        <div id="search-results"></div>
    </div>

    <script>
        const API_BASE = '/api';
        let authToken = localStorage.getItem('token') || '';

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            const res = await fetch(`${API_BASE}/auth/login/`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });

            const data = await res.json();
            if (data.token) {
                authToken = data.token;
                localStorage.setItem('token', authToken);
                document.getElementById('auth-status').textContent = `Logged in as ${data.user.username}`;
            } else {
                document.getElementById('auth-status').textContent = data.error;
            }
        }

        async function loadPosts() {
            const res = await fetch(`${API_BASE}/posts/`);
            const data = await res.json();

            const container = document.getElementById('posts-list');
            container.innerHTML = data.results.map(post => `
                <div class="post">
                    <h4>${post.title}</h4>
                    <p>By ${post.author.username} | Views: ${post.view_count}</p>
                    <p>${post.tags.map(t => `<span class="tag">${t}</span>`).join(' ')}</p>
                    <a href="${post.short_url}">Short URL</a>
                </div>
            `).join('');
        }

        async function searchPosts() {
            const query = document.getElementById('search-query').value;
            const res = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}`);
            const data = await res.json();

            document.getElementById('search-results').innerHTML = 
                `<p>Found ${data.count} results for "${data.query}"</p>` +
                data.results.map(r => `<div class="post"><h4>${r.title}</h4><p>Score: ${r.search_score}</p></div>`).join('');
        }

        // Auto-load token if exists
        if (authToken) {
            document.getElementById('auth-status').textContent = 'Token loaded from storage';
        }
    </script>
</body>
</html>
```

### DRF Note
Later: DRF's browsable API replaces this. But building it manually teaches you how APIs are consumed.

---

## DAY 11: Documentation + Docker + Polish

### Study (1 hr)
- **Docker:** `Dockerfile`, `docker-compose`, services.
- **README Best Practices:** Installation, usage, API reference.

### Build (4-5 hrs)

**Step 1: Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "blog_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**Step 2: docker-compose.yml**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: blog
      POSTGRES_USER: bloguser
      POSTGRES_PASSWORD: blogpass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgres://bloguser:blogpass@db:5432/blog

volumes:
  postgres_data:
```

**Step 3: requirements.txt**
```
Django>=5.0,<6.0
psycopg2-binary>=2.9
gunicorn>=21.0
```

**Step 4: Comprehensive README.md**

Write README.md with this structure:

```markdown
# Django Blog API with Algorithms

A production-ready blog API built with pure Django to master backend fundamentals before DRF.

## Algorithms Implemented

| Algorithm | Feature | Complexity |
|-----------|---------|------------|
| Base62 Encoding | Short URL generation | O(log_62 n) |
| Adjacency List + Recursion | Comment threading | O(n) subtree |
| TF-IDF | Search relevance ranking | O(D * V) index build |
| Cosine Similarity | Collaborative recommendations | O(n) per pair |
| LFU Cache | Popular posts caching | O(1) get/put |

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| /api/posts/ | GET/POST | POST only | List/create posts |
| /api/posts/<id>/ | GET/PUT/DELETE | PUT/DEL only | Post detail |
| /api/posts/<id>/comments/ | GET/POST | POST only | Comments |
| /api/search/?q= | GET | No | TF-IDF search |
| /api/recommendations/ | GET | Yes | Collaborative filtering |
| /api/posts/popular/ | GET | No | LFU cached popular |
| /api/auth/register/ | POST | No | User registration |
| /api/auth/login/ | POST | No | Token login |
| /s/<short_code>/ | GET | No | Short URL redirect |

## Quick Start

```bash
# Local
git clone <repo>
cd blog_project
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Docker
docker-compose up --build
```

## DRF Migration Path

This project is intentionally built without DRF. After completion:

1. Install `djangorestframework`
2. Replace manual serializers with `ModelSerializer`
3. Replace function views with `ModelViewSet`
4. Replace manual auth with `TokenAuthentication`
5. Add `django-filter` for advanced filtering

See DRF_MIGRATION.md for detailed mapping.
```

---

## DAY 12: Final Review + Interview Prep

### Morning (3 hrs): Code Review
- Review all algorithms. Ensure they have docstrings.
- Check for N+1 queries. Add `select_related`/`prefetch_related` where missing.
- Verify all endpoints return consistent JSON structure.
- Run full test suite: `python manage.py test`

### Afternoon (3 hrs): Interview Q&A Prep

**Base62:**
- Q: Why not Base64? A: URL-safe (no +, /, = padding issues).
- Q: Collision probability? A: Zero — bijective mapping.

**TF-IDF:**
- Q: Why not just count occurrences? A: IDF penalizes common words ("the", "and").
- Q: How to handle new documents? A: Rebuild index or use incremental updates.

**Collaborative Filtering:**
- Q: Cold start problem? A: New users have no likes — fall back to popular posts.
- Q: Scalability? A: Matrix factorization (SVD) for large user bases.

**LFU Cache:**
- Q: Why LFU over LRU? A: LFU keeps truly popular items; LRU keeps recently accessed.
- Q: Memory leak? A: Set capacity, evict on full.

---

## Final Project Summary

| Metric | Value |
|--------|-------|
| **Total Days** | 12 |
| **Daily Hours** | 5–6 |
| **Total Hours** | 60–72 |
| **Algorithms** | 5 |
| **API Endpoints** | 10+ |
| **Models** | 6 (User, Post, Tag, Comment, Like, APIToken) |
| **Tests** | 20+ unit tests |
| **DRF Prep Level** | High — every DRF feature has manual equivalent |

---

## What You Will Tell Interviewers

> "I built a full blog API in pure Django with 5 algorithms: Base62 for short URLs, adjacency lists for threaded comments, TF-IDF for search, cosine similarity for recommendations, and LFU cache for popular posts. I did this before touching DRF so I understand what serializers, viewsets, and authentication actually do under the hood."

---

**Ready to start Day 1?** I can generate the complete Day 1 code (models, Base62, admin, migrations) in a downloadable file, or walk you through it step by step.
