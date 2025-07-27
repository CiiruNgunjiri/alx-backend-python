from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Custom pagination for messages with default page size 20,
    override with 'page_size' query parameter up to max 100.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100