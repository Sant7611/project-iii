import django_filters
from blog.models import Post


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class PublicPostFilter(django_filters.FilterSet):
    @property
    def qs(self):
        return super().qs.distinct()

    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    categories = CharInFilter(field_name='categories__name', lookup_expr='in')
    tags = CharInFilter(field_name='tags__name', lookup_expr='in')

    class Meta:
        model = Post
        fields=[]
        
class MyPostFilter(PublicPostFilter):
    approval_status = django_filters.ChoiceFilter(field_name='approval_status', choices=Post.PostStatus.choices)