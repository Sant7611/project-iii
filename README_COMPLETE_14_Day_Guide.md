
readme_content = """# Django Blog System: DRF Foundation + Algorithms
# 14-Day Hybrid Build Guide (5-6 hrs/day)

> **No Redis, No Celery** — Pure Django + PostgreSQL/SQLite. Redis studied post-project.
> **Comment System:** Adjacency List (parent_id) — most popular, easiest to understand.
> **Days 1-9:** Pure Django (understand the foundations)
> **Days 10-11:** DRF Study (learn the abstractions)
> **Days 12-14:** DRF Migration (apply what you learned)

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
| API Style | Days 1-9: Pure Django JSON. Days 12-14: DRF |

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
│   ├── views.py           # Pure Django views (Days 1-9)
│   ├── drf_views.py       # DRF ViewSets (Days 12-14)
│   ├── serializers.py     # DRF Serializers (Days 12-14)
│   ├── urls.py            # API routes
│   ├── utils/
│   │   ├── base62.py      # Algorithm 1
│   │   ├── search.py      # Algorithm 3 (TF-IDF)
│   │   ├── recommender.py # Algorithm 4 (Collaborative Filtering)
│   │   └── cache.py       # Algorithm 5 (LFU Cache)
│   └── tests.py
├── users/
│   ├── models.py          # Custom User + APIToken
│   ├── views.py           # Pure Django auth
│   ├── drf_views.py       # DRF auth
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
curl -X POST http://localhost:8000/api/posts/ \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Hello","content":"World","tags":["django","api"]}'

curl http://localhost:8000/api/posts/
curl http://localhost:8000/s/1/
```

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
curl -X POST http://localhost:8000/api/posts/1/comments/ \\
  -H "Content-Type: application/json" \\
  -d '{"content":"Great post!"}'

curl -X POST http://localhost:8000/api/posts/1/comments/ \\
  -H "Content-Type: application/json" \\
  -d '{"content":"Thanks!","parent_id":1}'
```

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
        return re.findall(r'\b[a-z]+\b', text.lower())
    
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
curl -X POST http://localhost:8000/api/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{"username":"alice","password":"secret123"}'

curl -X POST http://localhost:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{"username":"alice","password":"secret123"}'

curl http://localhost:8000/api/posts/ \\
  -H "X-API-Token: <token_from_above>"
```

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

## DAY 10: DRF Study Day 1 — Serializers & ViewSets

### Study (3 hrs)
- **DRF Official Tutorial:** Parts 1-3 (serializers, requests/responses, class-based views)
- **Key Concepts:**
  - `Serializer` vs `ModelSerializer`
  - `APIView` vs `ViewSet`
  - `Response` vs `JsonResponse`
  - `status` module for HTTP codes

### Build (2-3 hrs)

**Step 1: Install DRF**
```bash
pip install djangorestframework
```

**Step 2: Update Settings**
```python
# blog_project/settings.py
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework.authtoken',  # For token auth later
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
```

**Step 3: Create Your First DRF Serializer (blog/serializers.py)**
```python
from rest_framework import serializers
from .models import Post, Tag, Comment

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    short_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'short_code', 'short_url', 
                  'content', 'author', 'status', 'view_count', 
                  'tags', 'created_at', 'updated_at']
        read_only_fields = ['short_code', 'view_count']
    
    def get_short_url(self, obj):
        return f'/s/{obj.short_code}/'
    
    def create(self, validated_data):
        # Custom create to handle tags
        tags_data = self.context.get('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            post.tags.add(tag)
        return post
```

**Step 4: Create Your First ViewSet (blog/drf_views.py)**
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tags')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'
    
    def get_queryset(self):
        # Filter by status for list view
        if self.action == 'list':
            return Post.objects.filter(status='published')
        return self.queryset
    
    def perform_create(self, serializer):
        # Automatically set author
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        # Increment view count on detail view
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Custom action to publish a draft post"""
        post = self.get_object()
        if post.author != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        post.status = 'published'
        post.save()
        return Response({'message': 'Post published'})
```

**Step 5: Wire Up DRF Router (blog/urls.py)**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Pure Django views (keep for comparison)
from . import drf_views  # DRF ViewSets

router = DefaultRouter()
router.register(r'posts', drf_views.PostViewSet, basename='post')

urlpatterns = [
    # Pure Django endpoints (for comparison)
    path('api/v1/posts/', views.post_list, name='post-list-legacy'),
    path('api/v1/posts/<int:pk>/', views.post_detail, name='post-detail-legacy'),
    
    # DRF endpoints
    path('api/v2/', include(router.urls)),
    
    # Other endpoints remain pure Django for now
    path('api/search/', views.search_posts, name='search'),
    path('api/posts/<int:post_id>/comments/', views.comment_list, name='comment-list'),
    path('api/posts/<int:post_id>/like/', views.like_post, name='like-post'),
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/posts/popular/', views.get_popular_posts, name='popular-posts'),
    path('s/<str:short_code>/', views.short_redirect, name='short-redirect'),
]
```

### Test DRF Endpoints
```bash
# Compare pure Django vs DRF
curl http://localhost:8000/api/v1/posts/
curl http://localhost:8000/api/v2/posts/

# DRF browsable API (visit in browser)
http://localhost:8000/api/v2/posts/

# Custom action
curl -X POST http://localhost:8000/api/v2/posts/1/publish/ \\
  -H "Authorization: Token <your_token>"
```

### Key Learning
Compare your Day 2 `post_list()` (20+ lines) with DRF's `PostViewSet` (5 lines). This is the "aha" moment.

---

## DAY 11: DRF Study Day 2 — Auth, Permissions, Nested Serializers

### Study (3 hrs)
- **DRF Authentication:** `TokenAuthentication`, `SessionAuthentication`, `BasicAuthentication`
- **Permissions:** `IsAuthenticated`, `IsOwner`, custom permissions
- **Nested Serializers:** Handling FK and M2M relationships
- **Filtering:** `django-filter` integration

### Build (2-3 hrs)

**Step 1: DRF Token Authentication (users/drf_views.py)**
```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def drf_register(request):
    """DRF version of register — compare with pure Django version"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username taken'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def drf_login(request):
    """DRF version of login — compare with pure Django version"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Delete old token, create new
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })
```

**Step 2: Custom Permission (blog/permissions.py)**
```python
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: only author can edit/delete.
    Compare with your manual check: request.user != post.author
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

**Step 3: Update PostViewSet with Permission**
```python
from .permissions import IsOwnerOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tags')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # ... rest same
```

**Step 4: Comment Serializer with Nesting (blog/serializers.py)**
```python
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'replies', 'created_at']
        read_only_fields = ['author']
    
    def get_replies(self, obj):
        # Recursive serialization — compare with your comment_to_dict()
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
```

**Step 5: Comment ViewSet (blog/drf_views.py)**
```python
from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('author', 'post')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Filter by post_id from URL
        post_id = self.kwargs.get('post_pk')
        if post_id:
            return self.queryset.filter(post_id=post_id, parent=None)
        return self.queryset
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        serializer.save(post_id=post_id)
```

**Step 6: Nested Router (blog/urls.py)**
```python
from rest_framework_nested import routers

# Main router
router = DefaultRouter()
router.register(r'posts', drf_views.PostViewSet)

# Nested router: /posts/{id}/comments/
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', drf_views.CommentViewSet, basename='post-comments')

urlpatterns = [
    path('api/v2/', include(router.urls)),
    path('api/v2/', include(posts_router.urls)),
    # ... other paths
]
```

### Test
```bash
# DRF auth
curl -X POST http://localhost:8000/api/v2/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{"username":"bob","password":"secret"}'

# DRF token login
curl -X POST http://localhost:8000/api/v2/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{"username":"bob","password":"secret"}'

# DRF nested comments
curl http://localhost:8000/api/v2/posts/1/comments/
```

---

## DAY 12: DRF Migration Day 1 — Convert Posts & Auth

### Goal
Replace pure Django views with DRF for Posts and Auth. Keep Search, Recommendations, and Popular as pure Django (they use custom algorithms).

### Build (5-6 hrs)

**Step 1: Final Post Serializer with All Fields**
```python
# blog/serializers.py (final version)
from rest_framework import serializers
from .models import Post, Tag, Comment, Like

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'replies', 'created_at']
    
    def get_replies(self, obj):
        if hasattr(obj, 'replies') and obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True, source='comments')
    short_url = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'short_code', 'short_url',
                  'content', 'author', 'status', 'view_count', 'like_count',
                  'is_liked', 'tags', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['short_code', 'view_count', 'like_count', 'is_liked']
    
    def get_short_url(self, obj):
        return f'/s/{obj.short_code}/'
    
    def get_like_count(self, obj):
        return obj.like_set.count()
    
            return obj.like_set.filter(user=request.user).exists()
        return False

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Separate serializer for write operations (tags as list of strings)"""
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'status', 'tags']
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
            post.tags.add(tag)
        return post
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
                instance.tags.add(tag)
        return instance
```

**Step 2: Final Post ViewSet with All Actions**
```python
# blog/drf_views.py (final version)
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment, Like
from .serializers import PostSerializer, PostCreateUpdateSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('tags', 'comments', 'like_set')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'author__username']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer
    
    def get_queryset(self):
        if self.action == 'list':
            return Post.objects.filter(status='published')
        return self.queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def publish(self, request, pk=None):
        post = self.get_object()
        if post.author != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        post.status = 'published'
        post.save()
        return Response({'status': 'published', 'short_url': f'/s/{post.short_code}/'})
    
    @action(detail=True, methods=['post', 'get'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            liked = Like.objects.filter(user=request.user, post=post).exists() if request.user.is_authenticated else False
            return Response({'liked': liked, 'count': post.like_set.count()})
        
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'liked': False, 'count': post.like_set.count()})
        return Response({'liked': True, 'count': post.like_set.count()})
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """List current user's posts (including drafts)"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """DRF version of popular posts - integrates with LFU cache"""
        from .views import rec_cache
        cached = rec_cache.get("popular")
        if cached:
            return Response({'cached': True, 'posts': cached})
        
        posts = Post.objects.filter(status='published').order_by('-view_count')[:10]
        serializer = PostSerializer(posts, many=True, context={'request': request})
        result = serializer.data
        rec_cache.put("popular", result)
        return Response({'cached': False, 'posts': result})
```

**Step 3: DRF Auth Views (users/drf_views.py - final)**
```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def drf_register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username taken'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def drf_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })

@api_view(['GET'])
def drf_profile(request):
    """Get current user profile"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'bio': request.user.bio,
        'avatar': request.user.avatar,
        'date_joined': request.user.created_at,
    })
```

**Step 4: Update Main URLs (blog_project/urls.py)**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('api/auth/', include('users.urls')),
]
```

**Step 5: Update Blog URLs (blog/urls.py - final)**
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views
from . import drf_views

# Main DRF router
router = DefaultRouter()
router.register(r'posts', drf_views.PostViewSet, basename='post')

# Nested router for comments
posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', drf_views.CommentViewSet, basename='post-comments')

urlpatterns = [
    # DRF API v2
    path('api/v2/', include(router.urls)),
    path('api/v2/', include(posts_router.urls)),
    
    # Pure Django endpoints (custom algorithms)
    path('api/search/', views.search_posts, name='search'),
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/posts/popular/', views.get_popular_posts, name='popular-posts'),
    
    # Short URL redirect
    path('s/<str:short_code>/', views.short_redirect, name='short-redirect'),
    
    # API docs
    path('api/', views.api_docs, name='api-docs'),
]
```

**Step 6: Update Users URLs (users/urls.py)**
```python
from django.urls import path
from . import drf_views

urlpatterns = [
    path('register/', drf_views.drf_register, name='drf-register'),
    path('login/', drf_views.drf_login, name='drf-login'),
    path('profile/', drf_views.drf_profile, name='drf-profile'),
]
```

**Step 7: Install django-filter**
```bash
pip install django-filter
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
]
```

### Test
```bash
# DRF browsable API
http://localhost:8000/api/v2/posts/

# Filter posts
http://localhost:8000/api/v2/posts/?search=django&ordering=-view_count

# Like via DRF
http://localhost:8000/api/v2/posts/1/like/

# My posts (including drafts)
http://localhost:8000/api/v2/posts/my_posts/

# Popular posts via DRF
http://localhost:8000/api/v2/posts/popular/
```

---

## DAY 13: DRF Migration Day 2 - Comments, Likes & Custom Actions

### Goal
Migrate Comments and Likes to DRF. Integrate custom algorithm endpoints (Search, Recommendations) with DRF Response format.

### Build (5-6 hrs)

**Step 1: Final Comment ViewSet with Recursive Replies**
```python
# blog/drf_views.py (add to existing file)
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Comment
from .serializers import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('author', 'post', 'parent')
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id:
            # Only top-level comments for list view
            if self.action == 'list':
                return self.queryset.filter(post_id=post_id, parent=None)
            return self.queryset.filter(post_id=post_id)
        return self.queryset
    
    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        parent_id = self.request.data.get('parent')
        
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post_id=post_id)
                serializer.save(post_id=post_id, author=self.request.user, parent=parent)
            except Comment.DoesNotExist:
                raise ValidationError({'parent': 'Parent comment not found'})
        else:
            serializer.save(post_id=post_id, author=self.request.user)
    
    def perform_update(self, serializer):
        if self.get_object().author != self.request.user:
            raise PermissionDenied('You can only edit your own comments')
        serializer.save()
    
    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Permission denied')
        instance.delete()
```

**Step 2: DRF-Style Search & Recommendation Endpoints**
```python
# blog/drf_views.py (add APIView-based algorithm endpoints)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class SearchAPIView(APIView):
    """DRF wrapper around TF-IDF search engine"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response({'error': 'Query too short (min 2 chars)'}, status=status.HTTP_400_BAD_REQUEST)
        
        from .views import search_engine, post_to_dict
        
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
        
        return Response({
            'query': query,
            'count': len(posts),
            'results': posts,
        })

class RecommendationAPIView(APIView):
    """DRF wrapper around collaborative filtering recommender"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        from .views import recommender, rec_cache, post_to_dict
        
        user_id = request.user.id
        cached = rec_cache.get(f"rec:{user_id}")
        if cached:
            return Response({'cached': True, 'results': cached})
        
        recommender.build_matrix(Like.objects.all())
        recs = recommender.recommend(user_id, n=5)
        
        results = []
        for post_id, score in recs:
            try:
                post = Post.objects.select_related('author').get(id=post_id)
                post_data = post_to_dict(post)
                post_data['recommendation_score'] = round(score, 4)
                results.append(post_data)
            except Post.DoesNotExist:
                continue
        
        rec_cache.put(f"rec:{user_id}", results)
        return Response({'cached': False, 'results': results})

class CacheStatsAPIView(APIView):
    """Debug endpoint to inspect LFU cache state"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        from .views import rec_cache
        return Response(rec_cache.get_stats())
```

**Step 3: Update URLs with DRF Algorithm Endpoints**
```python
# blog/urls.py (final)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views
from . import drf_views

router = DefaultRouter()
router.register(r'posts', drf_views.PostViewSet, basename='post')

posts_router = routers.NestedDefaultRouter(router, r'posts', lookup='post')
posts_router.register(r'comments', drf_views.CommentViewSet, basename='post-comments')

urlpatterns = [
    # DRF API v2
    path('api/v2/', include(router.urls)),
    path('api/v2/', include(posts_router.urls)),
    
    # DRF algorithm endpoints
    path('api/v2/search/', drf_views.SearchAPIView.as_view(), name='drf-search'),
    path('api/v2/recommendations/', drf_views.RecommendationAPIView.as_view(), name='drf-recommendations'),
    path('api/v2/cache-stats/', drf_views.CacheStatsAPIView.as_view(), name='cache-stats'),
    
    # Legacy pure Django endpoints (keep for comparison)
    path('api/search/', views.search_posts, name='search'),
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/posts/popular/', views.get_popular_posts, name='popular-posts'),
    path('s/<str:short_code>/', views.short_redirect, name='short-redirect'),
    path('api/', views.api_docs, name='api-docs'),
]
```

**Step 4: Add DRF Tests (blog/tests/test_drf.py)**
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from blog.models import Post, Tag, Comment, Like

User = get_user_model()

class DRFPostTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            status='published'
        )
    
    def test_list_posts(self):
        response = self.client.get('/api/v2/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_post(self):
        data = {
            'title': 'New Post',
            'content': 'New content',
            'status': 'published',
            'tags': ['django', 'test']
        }
        response = self.client.post('/api/v2/posts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')
        self.assertEqual(len(response.data['tags']), 2)
    
    def test_like_post(self):
        response = self.client.post(f'/api/v2/posts/{self.post.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        
        # Toggle off
        response = self.client.post(f'/api/v2/posts/{self.post.id}/like/')
        self.assertFalse(response.data['liked'])
    
    def test_publish_action(self):
        draft = Post.objects.create(title='Draft', content='Draft content', author=self.user, status='draft')
        response = self.client.post(f'/api/v2/posts/{draft.id}/publish/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        draft.refresh_from_db()
        self.assertEqual(draft.status, 'published')

class DRFCommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='commenter', password='pass')
        self.client.force_authenticate(user=self.user)
        
        self.author = User.objects.create_user(username='author', password='pass')
        self.post = Post.objects.create(title='Post', content='Content', author=self.author, status='published')
    
    def test_create_comment(self):
        data = {'content': 'Great post!'}
        response = self.client.post(f'/api/v2/posts/{self.post.id}/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Great post!')
    
    def test_nested_reply(self):
        parent = Comment.objects.create(post=self.post, author=self.author, content='Parent')
        data = {'content': 'Reply!', 'parent': parent.id}
        response = self.client.post(f'/api/v2/posts/{self.post.id}/comments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], parent.id)

class DRFAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_register(self):
        data = {'username': 'newuser', 'password': 'newpass123'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
    
    def test_login(self):
        User.objects.create_user(username='logintest', password='logpass')
        data = {'username': 'logintest', 'password': 'logpass'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
```

### Test
```bash
# Run all tests
python manage.py test blog.tests

# DRF browsable API with filtering
http://localhost:8000/api/v2/posts/?search=django&status=published

# Nested comments via DRF
http://localhost:8000/api/v2/posts/1/comments/

# Search via DRF
http://localhost:8000/api/v2/search/?q=python

# Recommendations via DRF
http://localhost:8000/api/v2/recommendations/

# Cache stats (debug)
http://localhost:8000/api/v2/cache-stats/
```

---

## DAY 14: Final Integration, Frontend & Deployment Prep

### Goal
Build minimal frontend consuming DRF API. Add final polish. Prepare for deployment.

### Study (2 hrs)
- **DRF Browsable API:** How it auto-generates forms from serializers.
- **CORS:** Why `django-cors-headers` is needed for separate frontend.
- **Production Checklist:** DEBUG=False, ALLOWED_HOSTS, static files, database.

### Build (3-4 hrs)

**Step 1: Install CORS Headers**
```bash
pip install django-cors-headers
```

```python
# settings.py
INSTALLED_APPS = [
    # ... existing
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... existing middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
]

# For development only
CORS_ALLOW_ALL_ORIGINS = True  # Remove in production
```

**Step 2: Minimal Frontend (templates/index.html)**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django Blog API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .endpoint { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; margin: 5px 0; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-right: 8px; }
        .get { background: #28a745; color: white; }
        .post { background: #007bff; color: white; }
        .put { background: #ffc107; color: black; }
        .delete { background: #dc3545; color: white; }
        .algo-badge { display: inline-block; background: #6f42c1; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px; }
        .feature-list { list-style: none; }
        .feature-list li { padding: 8px 0; border-bottom: 1px solid #eee; }
        .feature-list li:last-child { border-bottom: none; }
        .test-btn { background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        .test-btn:hover { background: #0056b3; }
        .result { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a { color: #007bff; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Django Blog System</h1>
        <p class="subtitle">DRF Foundation + 5 Custom Algorithms</p>
        
        <div class="nav">
            <a href="/api/v2/posts/">Browse API (DRF)</a>
            <a href="/api/">API Docs (JSON)</a>
            <a href="/admin/">Admin</a>
        </div>
        
        <div class="card">
            <h2>Features & Algorithms</h2>
            <ul class="feature-list">
                <li>
                    <strong>Short URLs</strong> <span class="algo-badge">Base62</span>
                    <div class="endpoint"><span class="get">GET</span> /s/{short_code}/</div>
                </li>
                <li>
                    <strong>Comment Threads</strong> <span class="algo-badge">Adjacency List + Recursive CTE</span>
                    <div class="endpoint"><span class="get">GET</span> /api/v2/posts/{id}/comments/</div>
                </li>
                <li>
                    <strong>Search</strong> <span class="algo-badge">TF-IDF</span>
                    <div class="endpoint"><span class="get">GET</span> /api/v2/search/?q={query}</div>
                </li>
                <li>
                    <strong>Recommendations</strong> <span class="algo-badge">Cosine Similarity</span>
                    <div class="endpoint"><span class="get">GET</span> /api/v2/recommendations/</div>
                </li>
                <li>
                    <strong>Popular Posts</strong> <span class="algo-badge">LFU Cache</span>
                    <div class="endpoint"><span class="get">GET</span> /api/v2/posts/popular/</div>
                </li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Quick Test</h2>
            <p>Fetch latest posts from the API:</p>
            <button class="test-btn" onclick="fetchPosts()">Fetch Posts</button>
            <div class="result" id="result">Click the button to test...</div>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <h3>Posts</h3>
            <div class="endpoint"><span class="get">GET</span> /api/v2/posts/ - List all published posts</div>
            <div class="endpoint"><span class="post">POST</span> /api/v2/posts/ - Create new post</div>
            <div class="endpoint"><span class="get">GET</span> /api/v2/posts/{id}/ - Get post detail</div>
            <div class="endpoint"><span class="put">PUT</span> /api/v2/posts/{id}/ - Update post</div>
            <div class="endpoint"><span class="delete">DELETE</span> /api/v2/posts/{id}/ - Delete post</div>
            <div class="endpoint"><span class="post">POST</span> /api/v2/posts/{id}/publish/ - Publish draft</div>
            <div class="endpoint"><span class="post">POST</span> /api/v2/posts/{id}/like/ - Toggle like</div>
            
            <h3>Comments</h3>
            <div class="endpoint"><span class="get">GET</span> /api/v2/posts/{id}/comments/ - List comments</div>
            <div class="endpoint"><span class="post">POST</span> /api/v2/posts/{id}/comments/ - Add comment</div>
            
            <h3>Auth</h3>
            <div class="endpoint"><span class="post">POST</span> /api/auth/register/ - Register</div>
            <div class="endpoint"><span class="post">POST</span> /api/auth/login/ - Login</div>
            <div class="endpoint"><span class="get">GET</span> /api/auth/profile/ - User profile</div>
        </div>
    </div>
    
    <script>
        async function fetchPosts() {
            const resultDiv = document.getElementById('result');
            resultDiv.textContent = 'Loading...';
            try {
                const response = await fetch('/api/v2/posts/');
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultDiv.textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
```

**Step 3: Add Template View (blog/views.py)**
```python
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
```

**Step 4: Update Root URL (blog_project/urls.py)**
```python
from django.contrib import admin
from django.urls import path, include
from blog.views import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('api/auth/', include('users.urls')),
]
```

**Step 5: Update Settings for Templates**
```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

**Step 6: Production Settings Checklist (settings_prod.py)**
```python
"""
Production settings - create this file and use it with:
DJANGO_SETTINGS_MODULE=blog_project.settings_prod python manage.py runserver
"""
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database - switch to PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog_db',
        'USER': 'blog_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# CORS - restrict in production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://yourfrontend.com",
]
```

**Step 7: Create requirements.txt**
```
Django>=5.0,<5.1
djangorestframework>=3.14
django-filter>=23.0
django-cors-headers>=4.0
psycopg2-binary>=2.9  # For PostgreSQL
```

**Step 8: Final Test Suite**
```bash
# Run all tests
python manage.py test blog.tests

# Test the full flow
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"finaltest","password":"finalpass"}'

# Login, get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"finaltest","password":"finalpass"}'

# Create post with token
curl -X POST http://localhost:8000/api/v2/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"title":"Final Test","content":"Testing complete system","status":"published","tags":["final","test"]}'

# Search
curl "http://localhost:8000/api/v2/search/?q=final"

# Like
curl -X POST http://localhost:8000/api/v2/posts/1/like/ \
  -H "Authorization: Token YOUR_TOKEN"

# Comment
curl -X POST http://localhost:8000/api/v2/posts/1/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"content":"Great post!"}'

# Recommendations (after likes exist)
curl http://localhost:8000/api/v2/recommendations/ \
  -H "Authorization: Token YOUR_TOKEN"

# Cache stats
curl http://localhost:8000/api/v2/cache-stats/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Final Project Structure

```
blog_project/
├── manage.py
├── requirements.txt
├── blog_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── settings_prod.py
│   ├── urls.py
│   └── wsgi.py
├── blog/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py           # Pure Django views (Search, Recommendations, Popular)
│   ├── drf_views.py       # DRF ViewSets + APIViews
│   ├── serializers.py     # DRF Serializers
│   ├── permissions.py     # Custom DRF permissions
│   ├── urls.py
│   ├── signals.py         # Search index rebuild signals
│   └── utils/
│       ├── base62.py
│       ├── search.py      # TF-IDF
│       ├── recommender.py # Collaborative Filtering
│       ├── cache.py       # LFU Cache
│       ├── serializers.py # Manual serializers (legacy)
│       └── response.py    # JSON response helper
│   └── tests/
│       ├── __init__.py
│       ├── test_base62.py
│       ├── test_search.py
│       ├── test_recommender.py
│       ├── test_cache.py
│       └── test_drf.py
├── users/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py           # Pure Django auth
│   ├── drf_views.py       # DRF auth
│   └── urls.py
└── templates/
    └── index.html
```

---

## What You Built

| Day | Topic | Key Output |
|-----|-------|-----------|
| 1 | Setup + Base62 | Working short URL system |
| 2 | Post CRUD | Manual JSON API with pagination |
| 3 | Comments | Recursive comment threading |
| 4 | Search | TF-IDF search engine |
| 5 | Likes | User-item matrix for CF |
| 6 | Recommendations + Cache | Cosine similarity + LFU cache |
| 7 | Auth | Token-based authentication |
| 8 | Testing | 4 algorithm test suites |
| 9 | DRF Prep | Migration guide + cleanup |
| 10 | DRF Study 1 | Post ViewSet + Router |
| 11 | DRF Study 2 | Auth, permissions, nested serializers |
| 12 | DRF Migration 1 | Posts + Auth fully DRF |
| 13 | DRF Migration 2 | Comments, algorithm APIViews |
| 14 | Integration | Frontend, CORS, production checklist |

---

## Interview Talking Points

1. **Base62:** "Bijective encoding ensures zero collisions. Time O(log_62 n)."
2. **Comments:** "Adjacency list with recursive CTE. Most scalable for read-heavy workloads."
3. **TF-IDF:** "Built inverted index from scratch. Understands TF, IDF, and relevance ranking."
4. **Collaborative Filtering:** "Cosine similarity on sparse user-item matrix. O(n) per pair."
5. **LFU Cache:** "O(1) get/put using hash map + frequency buckets. No Redis dependency."
6. **DRF Migration:** "Started with pure Django to understand foundations, then migrated to DRF to appreciate abstractions."

---

## Next Steps (Post-Project)

1. **Redis:** Replace in-memory LFU with Redis for distributed caching.
2. **Celery:** Offload TF-IDF index rebuilds to background tasks.
3. **Elasticsearch:** Replace in-memory search with ES for scale.
4. **React/Vue:** Build proper SPA frontend consuming the DRF API.
5. **Docker:** Containerize for deployment.
6. **Tests:** Add integration tests with `pytest-django`.

> **You now have a production-ready blog API with 5 custom algorithms and a complete DRF migration story. This is your portfolio project.**

"""
