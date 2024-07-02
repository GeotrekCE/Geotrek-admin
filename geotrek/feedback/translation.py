from modeltranslation.translator import translator, TranslationOptions

from geotrek.feedback import models as feedback_models


class ReportCategoryTO(TranslationOptions):
    all_fields = ('label',)


class ReportActivityTO(TranslationOptions):
    all_fields = ('label',)


class ReportProblemMagnitudeTO(TranslationOptions):
    all_fields = ('label',)


class ReportStatusTO(TranslationOptions):
    all_fields = ('label',)


translator.register(feedback_models.ReportCategory, ReportCategoryTO)
translator.register(feedback_models.ReportStatus, ReportStatusTO)
translator.register(feedback_models.ReportActivity, ReportActivityTO)
translator.register(feedback_models.ReportProblemMagnitude, ReportProblemMagnitudeTO)
