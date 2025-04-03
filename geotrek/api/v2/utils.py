from django.conf import settings
from modeltranslation.utils import build_localized_fieldname


def get_translation_or_dict(model_field_name, serializer, instance):
    """
    Return translated model field or dict with all translations
    :param model_field_name: Model name field
    :param serializer: serializer object
    :param instance: instance object
    :return: unicode or dict
    """
    lang = (
        serializer.context.get("request").GET.get("language", "all")
        if serializer.context.get("request")
        else "all"
    )

    if lang != "all":
        data = getattr(instance, build_localized_fieldname(model_field_name, lang))

    else:
        data = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            data.update(
                {
                    language: getattr(
                        instance, build_localized_fieldname(model_field_name, language)
                    )
                }
            )

    return data


def build_url(serializer, url):
    """
    Return the full url for a file or picture
    :param serializer: serializer object
    :param url: the ending url locating the file
    :return: full url
    """
    request = serializer.context.get("request", None)
    if request is not None and url[0] == "/":
        url = request.build_absolute_uri(url)
    else:
        raise Exception("Bad context. No server variable found in the request !")
    return url


def is_published(instance, language=None):
    """Returns the publication status of a publishabled model instance for the given language (with None or "all" for
    any language).

    - for a given language (for instance "fr") it returns the publication status for that language,
    - it handles model without a separate publication status for each language,
    - if language is None or "all" it returns True if the instance is published in at least one language.
    """
    associated_published_fields = [
        f.name for f in instance._meta.get_fields() if f.name.startswith("published")
    ]
    if len(associated_published_fields) == 1:
        # The instance's published field is not translated
        return instance.published
    elif len(associated_published_fields) > 1:
        # The published field is translated
        if not language or language == "all":
            # no language specified. Check for all.
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                field_name = build_localized_fieldname("published", lang)
                if getattr(instance, field_name):
                    break
            else:
                return False
            return True
        else:
            # one language is specified
            field_name = build_localized_fieldname("published", language)
            return getattr(instance, field_name)
