from modeltranslation.translator import TranslationOptions, translator

from geotrek.feedback import models as feedback_models


class ReportCategoryTO(TranslationOptions):
    fields = ("label",)


class ReportActivityTO(TranslationOptions):
    fields = ("label",)


class ReportProblemMagnitudeTO(TranslationOptions):
    fields = ("label",)


class ReportStatusTO(TranslationOptions):
    fields = ("label",)


translator.register(feedback_models.ReportCategory, ReportCategoryTO)
translator.register(feedback_models.ReportStatus, ReportStatusTO)
translator.register(feedback_models.ReportActivity, ReportActivityTO)
translator.register(feedback_models.ReportProblemMagnitude, ReportProblemMagnitudeTO)
