from django.contrib import admin

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.maintenance.models import (
    Contractor, InterventionStatus, InterventionType, InterventionDisorder,
    ProjectType, ProjectDomain, InterventionJob,
)


@admin.register(Contractor)
class ContractorAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('contractor', 'structure')
    search_fields = ('contractor', 'structure')
    list_filter = ('structure',)
    merge_field = "contractor"


@admin.register(InterventionStatus)
class InterventionStatusAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('status', 'order', 'structure')
    search_fields = ('status', 'order', 'structure')
    list_filter = ('structure',)
    merge_field = "status"


@admin.register(InterventionType)
class InterventionTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)
    merge_field = "type"


@admin.register(InterventionDisorder)
class InterventionDisorderAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('disorder', 'structure')
    search_fields = ('disorder', 'structure')
    list_filter = ('structure',)
    merge_field = "disorder"


@admin.register(InterventionJob)
class InterventionJobAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('job', 'cost', 'structure', 'active')
    search_fields = ('job', 'structure')
    list_filter = ('structure', 'active')
    merge_field = "job"


@admin.register(ProjectType)
class ProjectTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)
    merge_field = "type"


@admin.register(ProjectDomain)
class ProjectDomainAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('domain', 'structure')
    search_fields = ('domain', 'structure')
    list_filter = ('structure',)
    merge_field = "domain"
