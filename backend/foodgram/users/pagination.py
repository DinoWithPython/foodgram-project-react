from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Задаём пагинацию здесь."""
    page_size = 6
    page_size_query_param = 'limit'
    max_page_size = 12
