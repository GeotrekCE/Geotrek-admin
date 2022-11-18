from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.cache.mixins import RetrieveCacheResponseMixin as BaseRetrieveCacheResponseMixin


class RetrieveCacheResponseMixin(BaseRetrieveCacheResponseMixin):
    @cache_response(key_func='object_cache_key_func', timeout='object_cache_timeout', cache='api_v2')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
