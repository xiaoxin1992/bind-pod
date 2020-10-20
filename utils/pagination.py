from django.core.paginator import EmptyPage
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.conf import settings


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        try:
            previous_page = self.page.previous_page_number()
        except EmptyPage:
            previous_page = self.page.number

        try:
            next_page = self.page.next_page_number()
        except EmptyPage:
            next_page = self.page.number
        return Response({"data": {
            'page_num': {
                'next': next_page,
                'count_page': self.page.paginator.num_pages,
                'previous': previous_page,
                'count': self.page.paginator.count
            },
            'data': data
        }, "code": 200})
