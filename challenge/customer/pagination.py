from rest_framework import pagination

class CustomerListPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = 30