from modeltranslation.translator import translator, TranslationOptions

from geotrek.common.models import AnnotationCategory, TargetPortal, Theme, Label, HDViewPoint


class ThemeTO(TranslationOptions):
    fields = ('label', )


class AnnotationCategoryTO(TranslationOptions):
    fields = ('label', )


class TargetPortalTO(TranslationOptions):
    fields = ('title', 'description')


class LabelTO(TranslationOptions):
    fields = ('name', 'advice')


class HDViewPointTO(TranslationOptions):
    fields = ('title', 'legend')


translator.register(Theme, ThemeTO)
translator.register(TargetPortal, TargetPortalTO)
translator.register(Label, LabelTO)
translator.register(AnnotationCategory, AnnotationCategoryTO)
translator.register(HDViewPoint, HDViewPointTO)
