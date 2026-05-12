from django.core.cache import caches
from mapentity.settings import app_settings


def cbv_cache_response_content():
    """Decorator to cache the response content of a Class Based View"""

    def decorator(view_func):
        def _wrapped_method(self, *args, **kwargs):
            response_class = self.response_class
            response_kwargs = dict()

            # Restore from cache or store view result
            geojson_lookup = None
            if hasattr(self, "view_cache_key"):
                geojson_lookup = self.view_cache_key()

            geojson_cache = caches[app_settings["GEOJSON_LAYERS_CACHE_BACKEND"]]

            if geojson_lookup:
                content = geojson_cache.get(geojson_lookup)
                if content:
                    return response_class(content=content, **response_kwargs)

            response = view_func(self, *args, **kwargs)
            if geojson_lookup:
                geojson_cache.set(geojson_lookup, response.content)
            return response

        return _wrapped_method

    return decorator
