from modeltranslation.translator import translator, TranslationOptions
from geotrek.outdoor.models import Site


class SiteTO(TranslationOptions):
    fields = ('name', )


translator.register(Site, SiteTO)
