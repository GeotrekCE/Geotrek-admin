from rest_framework_extensions.cache.mixins import RetrieveCacheResponseMixin as BaseRetrieveCacheResponseMixin

from geotrek.api.v2.decorators import cache_response_detail


class RetrieveCacheResponseMixin(BaseRetrieveCacheResponseMixin):
    @cache_response_detail()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
