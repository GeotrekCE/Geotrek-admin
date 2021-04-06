from django.conf import settings
from django.db.models import Q


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


def filter_queryset_related_objects_published(queryset, request, prefix):
    """
    Return a queryset filtered by publication status or related objects.
    For example for a queryset of DifficultyLevels it will check the publication status of related treks and return the queryset of difficulties that are used by publisehd treks.
    :param queryset: the queryset to filter
    :param request: the request object to get to the potential language to filter by
    :param prefix: the prefix used to fetch the related object in the filter method
    """
    qs = queryset
    language = request.GET.get('language', 'all')
    if language == 'all':
        # no language specified. Check for all.
        q = Q()
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            related_field_name = '{}__published_{}'.format(prefix, lang)
            q |= Q(**{related_field_name: True})
        qs = qs.filter(q)
    else:
        # one language is specified
        related_field_name = '{}__published_{}'.format(prefix, language)
        qs = qs.filter(Q(**{related_field_name: True}))
    return qs.distinct()
