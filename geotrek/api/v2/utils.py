from __future__ import unicode_literals

from django.conf import settings


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
