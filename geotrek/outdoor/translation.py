from modeltranslation.translator import translator, TranslationOptions
from geotrek.outdoor.models import Site, Practice, SitePractice


class SiteTO(TranslationOptions):
    fields = ('name', )


class SitePracticeTO(TranslationOptions):
    fields = ('description_teaser', 'description', 'ambiance', 'advice', 'period')


class PracticeTO(TranslationOptions):
    fields = ('name', )


translator.register(Site, SiteTO)
translator.register(Practice, PracticeTO)
translator.register(SitePractice, SitePracticeTO)
