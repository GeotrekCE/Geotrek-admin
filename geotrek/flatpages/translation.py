from django.conf import settings

from modeltranslation.translator import translator, TranslationOptions

from geotrek.flatpages import models as flatpages_models


class FlatPageTO(TranslationOptions):
    fields = ('title', 'content', 'external_url') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple()
    )


translator.register(flatpages_models.FlatPage, FlatPageTO)
