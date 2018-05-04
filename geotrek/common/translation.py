from modeltranslation.translator import translator, TranslationOptions

from geotrek.common.models import Theme


class ThemeTO(TranslationOptions):
    fields = ('label', )


translator.register(Theme, ThemeTO)
