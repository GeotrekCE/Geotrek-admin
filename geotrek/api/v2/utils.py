from django.conf import settings
from django.core.cache import caches
from rest_framework.response import Response


def get_translation_or_dict(model_field_name, serializer, instance):
    """
    Return translated model field or dict with all translations
    :param model_field_name: Model name field
    :param serializer: serializer object
    :param instance: instance object
    :return: unicode or dict
    """
    lang = serializer.context.get('request').GET.get('language', 'all') if serializer.context.get('request') else 'all'

    if lang != 'all':
        data = getattr(instance, '{}_{}'.format(model_field_name, lang))

    else:
        data = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            data.update({language: getattr(instance, '{}_{}'.format(model_field_name, language), )})

    return data


def build_url(serializer, url):
    """
    Return the full url for a file or picture
    :param serializer: serializer object
    :param url: the ending url locating the file
    :return: full url
    """
    request = serializer.context.get('request', None)
    if request is not None and url[0] == '/':
        url = request.build_absolute_uri(url)
    else:
        raise Exception('Bad context. No server variable found in the request !')
    return url


def build_response_from_cache(cache_lookup, data_func, content_type):
    # Choose adequate cache
    if content_type == "application/json":
        cache = caches[settings.MAPENTITY_CONFIG['GEOJSON_LAYERS_CACHE_BACKEND']]
    else:
        cache = caches['default']
    # Retrieve data from cache
    content = cache.get(cache_lookup)
    if content:
        return Response(content, content_type=content_type)
    # Or set data to cache
    content = data_func()
    cache.set(cache_lookup, content)
    return Response(content, content_type=content_type)
