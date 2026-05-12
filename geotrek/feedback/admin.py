from django.conf import settings
from django.contrib import admin

from geotrek.feedback import models as feedback_models

if "modeltranslation" in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin


class WorkflowManagerAdmin(admin.ModelAdmin):
    """
    Workflow Manager is a User that is responsible for assigning reports to other Users and confirming that reports can be marked as resolved
    There should be only one Workflow Manager, who will receive notification emails when an action is needed
    """

    def has_add_permission(self, request):
        # There can be only one manager
        perms = super().has_add_permission(request)
        if perms and (
            not settings.SURICATE_WORKFLOW_ENABLED
            or feedback_models.WorkflowManager.objects.exists()
        ):
            perms = False  # Disallow creating a new workflow manager if there is one already
        return perms


class WorkflowDistrictAdmin(admin.ModelAdmin):
    """
    Workflow District is a District that defines the zone in which reports should be handled through Suricate workflow
    There should be only one Workflow District
    """

    def has_add_permission(self, request):
        # There can be only one district
        perms = super().has_add_permission(request)
        if perms and (
            not settings.SURICATE_WORKFLOW_ENABLED
            or feedback_models.WorkflowDistrict.objects.exists()
        ):
            perms = False  # Disallow creating a new workflow district if there is one already
        return perms


class PredefinedEmailAdmin(admin.ModelAdmin):
    """
    Workflow District is a District that defines the zone in which reports should be handled through Suricate workflow
    There should be only one Workflow District
    """

    def has_add_permission(self, request):
        # There can be only one district
        perms = super().has_add_permission
        return perms and settings.SURICATE_WORKFLOW_ENABLED


admin.site.register(feedback_models.ReportCategory, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportStatus)
admin.site.register(feedback_models.ReportActivity, TabbedTranslationAdmin)
admin.site.register(feedback_models.ReportProblemMagnitude, TabbedTranslationAdmin)
admin.site.register(feedback_models.PredefinedEmail, PredefinedEmailAdmin)
admin.site.register(feedback_models.WorkflowManager, WorkflowManagerAdmin)
admin.site.register(feedback_models.WorkflowDistrict, WorkflowDistrictAdmin)
