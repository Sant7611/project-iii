from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Post(models.Model):
    """
    The core content model.
    
    DESIGN CHOICES EXPLAINED:
    - status: 'draft' vs 'published' allows authors to work on posts before they go live.
    - slug: SEO-friendly URL piece. Auto-generated from title.
    - short_code: Generated AFTER save (via Base62) so we can use the post ID.
    - featured_img: Kept from your design! Good addition. upload_to organizes files.
    - user -> renamed to 'author' for clarity (author writes, user reads).
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    featured_img = models.ImageField(upload_to='posts/%Y/%m/', blank=True, null=True)
    # share_code renamed to short_code to match the Base62 algorithm guide
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            base_slug = slugify(self.title)[:50]
            slug = base_slug
            counter = 1
            # Ensure uniqueness — if "hello-world" exists, try "hello-world-1"
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
        # # Generate short_code AFTER first save, because we need the auto-assigned ID
        # if not self.short_code:
            
        #     self.short_code = encode(self.id)
        #     self.save(update_fields=['short_code'])
    
    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Kept from your design! Categories are broader buckets than tags.
    Example: "Technology", "Lifestyle". A post can belong to multiple categories.
    """
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name='categories')
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags are specific keywords. "django", "python", "tutorial".
    """
    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name='tags')
    
    def __str__(self):
        return self.name

class Comment(models.Model):
    """
    Adjacency List pattern for threaded comments.
    
    WHY Adjacency List?
    - Each comment stores a parent_id referencing another comment.
    - Simple, flexible, and the most common pattern (Reddit, Disqus, WordPress).
    - parent=None means it's a top-level comment.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Like(models.Model):
    """
    A user likes a post.
    
    CRITICAL FIX: Previously used OneToOneField on user.
    OneToOne means: ONE user can have ONE like. That's wrong.
    A user should be able to like MANY posts, but only ONCE per post.
    
    FIX: Use ForeignKey + unique_together = ['user', 'post']
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        # This prevents duplicate likes: one user can only like a post once.
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
