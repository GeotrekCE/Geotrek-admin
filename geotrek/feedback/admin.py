from django.contrib import admin
from django.conf import settings

from geotrek.feedback import models as feedback_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


admin.site.register(feedback_models.ReportCategory, TranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
admin.site.register(feedback_models.ReportActivity, TranslationAdmin)
admin.site.register(feedback_models.ReportProblemMagnitude, TranslationAdmin)
