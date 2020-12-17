from django.conf import settings
from geotrek.outdoor.models import Site, Practice
from modeltranslation.translator import translator, TranslationOptions


class SiteTO(TranslationOptions):
    fields = ('name', 'description', 'description_teaser', 'ambiance', 'advice', 'period') + (
        ('published',) if settings.PUBLISHED_BY_LANG else tuple())
    fallback_undefined = {'published': None}


class PracticeTO(TranslationOptions):
    fields = ('name', )


translator.register(Site, SiteTO)
translator.register(Practice, PracticeTO)
