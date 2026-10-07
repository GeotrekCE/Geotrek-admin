from django.conf import settings
from django.contrib import admin

from . import models

if "modeltranslation" in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin

if settings.REPORT_MODEL_ENABLED:

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
                or models.WorkflowManager.objects.exists()
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
                or models.WorkflowDistrict.objects.exists()
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

    admin.site.register(models.ReportCategory, TabbedTranslationAdmin)
    admin.site.register(models.ReportStatus)
    admin.site.register(models.ReportActivity, TabbedTranslationAdmin)
    admin.site.register(models.ReportProblemMagnitude, TabbedTranslationAdmin)
    admin.site.register(models.PredefinedEmail, PredefinedEmailAdmin)
    admin.site.register(models.WorkflowManager, WorkflowManagerAdmin)
    admin.site.register(models.WorkflowDistrict, WorkflowDistrictAdmin)
