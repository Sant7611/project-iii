from rest_framework.pagination import PageNumberPagination


class PageNumPagination(PageNumberPagination):
    page_size = 5
    page_query_param='page-num'
    page_size_query_param='page-size'
    max_page_size = '10'