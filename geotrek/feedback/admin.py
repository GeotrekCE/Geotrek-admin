from django.conf import settings
from django.contrib import admin

from geotrek.feedback import models as feedback_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin


class WorkflowManagerAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        # There can be only one manager
        perms = super().has_add_permission(request)
        if perms and feedback_models.WorkflowManager.objects.exists():
            perms = False
        return perms


admin.site.register(feedback_models.WorkflowManager, WorkflowManagerAdmin)
admin.site.register(feedback_models.ReportCategory, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
admin.site.register(feedback_models.ReportActivity, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportProblemMagnitude, TabbedTranslationAdmin)
