from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

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
            return super(StandardResultsSetPagination, self).get_paginated_response(data)
