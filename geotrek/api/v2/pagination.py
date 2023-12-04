from collections import OrderedDict

from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FasterPaginator(Paginator):
    @cached_property
    def count(self):
        """ As object_list is evaluated in pagination, just count element instead of SQL COUNT """
        qs = self.object_list.values('pk').order_by()
        return qs.count()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000
    django_paginator_class = FasterPaginator

    def get_paginated_response(self, data):
        if self.request.query_params.get('format', 'json') == 'geojson':
            return Response(OrderedDict([
                ('type', 'FeatureCollection'),
                ('count', self.page.paginator.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('features', data['features'])
            ]))
        else:
            return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        if 'no_page' in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)
