from modeltranslation.translator import translator, TranslationOptions

from geotrek.feedback import models as feedback_models


class ReportCategoryTO(TranslationOptions):
    fields = ('category',)


translator.register(feedback_models.ReportCategory, ReportCategoryTO)
