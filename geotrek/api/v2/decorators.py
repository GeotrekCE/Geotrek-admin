from rest_framework_extensions.cache.decorators import CacheResponse as BaseCacheResponse


class APIV2CacheResponseDetail(BaseCacheResponse):
    def __init__(self,
                 timeout='object_cache_timeout',
                 key_func='object_cache_key_func',
                 cache='api_v2',
                 cache_errors=None):
        super().__init__(timeout='object_cache_timeout',
                         key_func='object_cache_key_func',
                         cache='api_v2',
                         cache_errors=None)


cache_response_detail = APIV2CacheResponseDetail


class APIV2CacheResponseList(BaseCacheResponse):
    def __init__(self,
                 timeout='object_cache_timeout',
                 key_func='object_cache_key_func',
                 cache='api_v2',
                 cache_errors=None):
        super().__init__(timeout='list_cache_timeout',
                         key_func='list_cache_key_func',
                         cache='api_v2',
                         cache_errors=None)


cache_response_list = APIV2CacheResponseList
