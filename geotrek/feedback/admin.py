from django.conf import settings
from django.contrib import admin

from geotrek.feedback import models as feedback_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


admin.site.register(feedback_models.ReportCategory, TranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
