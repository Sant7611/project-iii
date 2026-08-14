from django.db import models
from django.conf import settings
from django.utils.text import slugify
from base.models import BaseModel


class Post(BaseModel):
    """
    The core content model.

    DESIGN CHOICES EXPLAINED:
    - status: 'draft' vs 'published' allows authors to work on posts before they go live.
    - slug: SEO-friendly URL piece. Auto-generated from title.
    - short_code: Generated AFTER save (via Base62) so we can use the post ID.
    - featured_img: Kept from your design! Good addition. upload_to organizes files.
    - user -> renamed to 'author' for clarity (author writes, user reads).
    """

    class PostStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED= "rejected", 'Rejected'

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    featured_img = models.ImageField(upload_to="posts/", blank=True, null=True)
    short_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    view_count = models.PositiveIntegerField(default=0)
    approval_status = models.CharField(
        choices=PostStatus.choices, default=PostStatus.PENDING, max_length=20
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_posts",
        limit_choices_to=models.Q(role="moderator")
        | models.Q(role="super_admin"),
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

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

    def __str__(self):
        return self.title


class Category(BaseModel):
    """
    Kept from your design! Categories are broader buckets than tags.
    Example: "Technology", "Lifestyle". A post can belong to multiple categories.
    """

    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name="categories")

    def __str__(self):
        return self.name


class Tag(BaseModel):
    """
    Tags are specific keywords. "django", "python", "tutorial".
    """

    name = models.CharField(max_length=50, unique=True)
    posts = models.ManyToManyField(Post, related_name="tags")

    def __str__(self):
        return self.name


class Comment(BaseModel):
    """
    Adjacency List pattern for threaded comments.

    WHY Adjacency List?
    - Each comment stores a parent_id referencing another comment.
    - Simple, flexible, and the most common pattern (Reddit, Disqus, WordPress).
    - parent=None means it's a top-level comment.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post} - {self.content}"


class Like(BaseModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "post"]
        # This prevents duplicate likes: one user can only like a post once.

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class SavedPost(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,  related_name='saved_by')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_saved_post_per_user",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} saved {self.post}"