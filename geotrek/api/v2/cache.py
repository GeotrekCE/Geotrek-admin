from rest_framework_extensions.cache.mixins import (
    ListCacheResponseMixin as BaseListCacheResponseMixin,
)
from rest_framework_extensions.cache.mixins import (
    RetrieveCacheResponseMixin as BaseRetrieveCacheResponseMixin,
)

from geotrek.api.v2.decorators import cache_response_detail, cache_response_list


class RetrieveCacheResponseMixin(BaseRetrieveCacheResponseMixin):
    @cache_response_detail()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ListCacheResponseMixin(BaseListCacheResponseMixin):
    @cache_response_list()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
