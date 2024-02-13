
from rest_framework.pagination import CursorPagination

class TestHistoryPagination(CursorPagination):
    page_size = 10
    ordering = '-date'