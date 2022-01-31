import json
from django.conf import settings
from django.core.cache import caches
from mapentity.views.mixins import HttpJSONResponse
from geotrek.altimetry.views import HttpSVGResponse


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


def cached_json_response(cache_lookup, data_func):
    json_cache = caches[settings.MAPENTITY_CONFIG['GEOJSON_LAYERS_CACHE_BACKEND']]
    content = json_cache.get(cache_lookup)
    if content:
        return HttpJSONResponse(content=content)
    elevation_area_json = json.dumps(data_func())
    json_cache.set(cache_lookup, elevation_area_json)
    response = HttpJSONResponse(elevation_area_json)
    return response


def cached_svg_response(cache_lookup, data_func, lang, **kwargs):
    svg_cache = caches['default']
    content = svg_cache.get(cache_lookup)
    if content:
        return HttpSVGResponse(content=content, **kwargs)
    profile_svg = data_func(lang)
    svg_cache.set(cache_lookup, profile_svg)
    return HttpSVGResponse(profile_svg, **kwargs)
