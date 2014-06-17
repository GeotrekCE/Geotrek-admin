from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from geotrek.feedback import models as feedback_models


admin.site.register(feedback_models.ReportCategory, TranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
