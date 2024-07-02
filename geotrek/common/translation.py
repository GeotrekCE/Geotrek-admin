from modeltranslation.translator import translator, TranslationOptions

from geotrek.common.models import TargetPortal, Theme, Label, HDViewPoint


class ThemeTO(TranslationOptions):
    all_fields = ('label', )


class TargetPortalTO(TranslationOptions):
    all_fields = ('title', 'description')


class LabelTO(TranslationOptions):
    all_fields = ('name', 'advice')


class HDViewPointTO(TranslationOptions):
    all_fields = ('title', 'legend')


translator.register(Theme, ThemeTO)
translator.register(TargetPortal, TargetPortalTO)
translator.register(Label, LabelTO)
translator.register(HDViewPoint, HDViewPointTO)
