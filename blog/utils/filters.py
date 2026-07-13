import django_filters
from blog.models import Post


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass

class PostFilter(django_filters.FilterSet):
    @property
    def qs(self):
        return super().qs.distinct()

    author = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    published = django_filters.BooleanFilter(field_name='is_published')
    categories = CharInFilter(field_name='categories__name', lookup_expr='in')
    tags = CharInFilter(field_name='tags__name', lookup_expr='in')

    class Meta:
        model = Post
        fields=[]