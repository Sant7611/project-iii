from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    featured_img = models.ImageField()
    share_code = models.TextField(max_length=50)
    view_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)




    def __str__(self):
        return self.title
    

class Category(models.Model):
    name = models.TextField(max_length=50)
    posts = models.ManyToManyField(Post, related_name='categories')

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.TextField(max_length=50)
    posts = models.ManyToManyField(Post, related_name='tags')

    def __str__(self):
        return self.name
    
class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', related_name='replies')
    post = models.ForeignKey(Post, related_name='comments')
    # user = models.ForeignKey(User)

# post_id (FK → POST.post_id)
# user_id (FK → USER.user_id)
# parent_comment_id (FK → COMMENT.comment_id, nullable)
# content
# created_at
# updated_at