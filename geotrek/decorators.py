from django.core.cache import caches
from mapentity.settings import app_settings


def cbv_cache_response_content():
    """ Decorator to cache the response content of a Class Based View """
    def decorator(view_func):
        def _wrapped_method(self, *args, **kwargs):
            response_class = self.response_class
            response_kwargs = dict()

            # Do not cache if filters presents
            params = self.request.GET.keys()
            with_filters = all([not p.startswith('_') for p in params])
            if len(params) > 0 and with_filters:
                return view_func(self, *args, **kwargs)

            # Restore from cache or store view result
            geojson_lookup = None
            if hasattr(self, 'view_cache_key'):
                geojson_lookup = self.view_cache_key()
            elif not self.request.GET:  # Do not cache filtered responses
                view_model = self.get_model()
                language = self.request.LANGUAGE_CODE
                latest_saved = view_model.latest_updated()
                if latest_saved:
                    geojson_lookup = '%s_%s_%s_json_layer' % (
                        language,
                        view_model._meta.model_name,
                        latest_saved.strftime('%y%m%d%H%M%S%f')
                    )

            geojson_cache = caches[app_settings['GEOJSON_LAYERS_CACHE_BACKEND']]

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
