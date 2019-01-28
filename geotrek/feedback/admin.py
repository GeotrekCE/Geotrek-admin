from django.contrib import admin

from geotrek.feedback import models as feedback_models

from modeltranslation.admin import TranslationAdmin


admin.site.register(feedback_models.ReportCategory, TranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
