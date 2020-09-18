from modeltranslation.translator import translator, TranslationOptions

from geotrek.common.models import TargetPortal, Theme


class ThemeTO(TranslationOptions):
    fields = ('label', )


class TargetPortalTO(TranslationOptions):
    fields = ('title', 'description')


translator.register(Theme, ThemeTO)
translator.register(TargetPortal, TargetPortalTO)
