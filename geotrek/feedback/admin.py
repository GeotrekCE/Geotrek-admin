from django.contrib import admin
from django.conf import settings

from geotrek.feedback import models as feedback_models

if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin
else:
    TranslationAdmin = admin.ModelAdmin


class WorkflowManagerAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        # There can be only one manager
        perms = super().has_add_permission(request)
        if perms and feedback_models.WorkflowManager.objects.exists():
            perms = False
        return perms


admin.site.register(feedback_models.ReportCategory, TranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
admin.site.register(feedback_models.WorkflowManager, WorkflowManagerAdmin)
admin.site.register(feedback_models.ReportActivity, TranslationAdmin)
admin.site.register(feedback_models.ReportProblemMagnitude, TranslationAdmin)
