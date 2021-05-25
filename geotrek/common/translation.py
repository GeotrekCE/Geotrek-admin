from modeltranslation.translator import translator, TranslationOptions

from geotrek.common.models import TargetPortal, Theme, Label


class ThemeTO(TranslationOptions):
    fields = ('label', )


class TargetPortalTO(TranslationOptions):
    fields = ('title', 'description')


class LabelTO(TranslationOptions):
    fields = ('name', 'advice')


translator.register(Theme, ThemeTO)
translator.register(TargetPortal, TargetPortalTO)
translator.register(Label, LabelTO)
