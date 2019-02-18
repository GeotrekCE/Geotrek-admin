from __future__ import unicode_literals

from geotrek.api.mobile import pagination as api_pagination_mobile
from geotrek.api.v2.viewsets import GeotrekViewset


class MobileViewset(GeotrekViewset):
    pagination_class = api_pagination_mobile.StandardResultsSetPagination
