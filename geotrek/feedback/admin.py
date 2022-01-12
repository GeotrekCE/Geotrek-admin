from django.contrib import admin
from django.conf import settings

from geotrek.feedback import models as feedback_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    TabbedTranslationAdmin = admin.ModelAdmin


admin.site.register(feedback_models.ReportCategory, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
admin.site.register(feedback_models.ReportActivity, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportProblemMagnitude, TabbedTranslationAdmin)
