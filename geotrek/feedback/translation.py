from modeltranslation.translator import translator, TranslationOptions

from geotrek.feedback import models as feedback_models


class ReportCategoryTO(TranslationOptions):
    fields = ('category',)


class ReportActivityTO(TranslationOptions):
    fields = ('activity',)


class ReportProblemMagnitudeTO(TranslationOptions):
    fields = ('magnitude',)


translator.register(feedback_models.ReportCategory, ReportCategoryTO)
translator.register(feedback_models.ReportActivity, ReportActivityTO)
translator.register(feedback_models.ReportProblemMagnitude, ReportProblemMagnitudeTO)
