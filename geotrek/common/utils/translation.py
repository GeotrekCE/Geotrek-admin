from django.conf import settings

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.translator import translator, NotRegistered


def get_translated_fields(model):
    """Get translated fields from a model"""
    try:
        mto = translator.get_options_for_model(model)
    except NotRegistered:
        translated_fields = []
    else:
        return list(mto.fields)
    return translated_fields
