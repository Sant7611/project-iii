def post_to_dict(post):
    """Convert a Post model to a JSON-serializable dictionary."""
    return {
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "short_code": post.short_code,
        "content": post.content,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
        },
        "is_published": post.is_published,
        "view_count": post.view_count,
        "featured_img": post.featured_img.url if post.featured_img else None,
        "tags": [tag.name for tag in post.tags.all()],
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }

def comment_to_dict(comment):
    return {
        'id': comment.id,
        'author': comment.author.username,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'replies': [comment_to_dict(reply) for reply in comment.replies.all()],
    }
