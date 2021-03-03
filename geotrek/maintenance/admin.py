from django.contrib import admin

from geotrek.common.mixins import MergeActionMixin
from geotrek.maintenance.models import (
    Contractor, InterventionStatus, InterventionType, InterventionDisorder,
    ProjectType, ProjectDomain, InterventionJob,
)


class ContractorAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('contractor', 'structure')
    search_fields = ('contractor', 'structure')
    list_filter = ('structure',)
    merge_field = "contractor"


class InterventionStatusAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('status', 'order', 'structure')
    search_fields = ('status', 'order', 'structure')
    list_filter = ('structure',)
    merge_field = "status"


class InterventionTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)
    merge_field = "type"


class InterventionDisorderAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('disorder', 'structure')
    search_fields = ('disorder', 'structure')
    list_filter = ('structure',)
    merge_field = "disorder"


class InterventionJobAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('job', 'cost', 'structure')
    search_fields = ('job', 'structure')
    list_filter = ('structure',)
    merge_field = "job"


class ProjectTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)
    merge_field = "type"


class ProjectDomainAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('domain', 'structure')
    search_fields = ('domain', 'structure')
    list_filter = ('structure',)
    merge_field = "domain"


admin.site.register(Contractor, ContractorAdmin)
admin.site.register(InterventionStatus, InterventionStatusAdmin)
admin.site.register(InterventionType, InterventionTypeAdmin)
admin.site.register(InterventionDisorder, InterventionDisorderAdmin)
admin.site.register(InterventionJob, InterventionJobAdmin)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(ProjectDomain, ProjectDomainAdmin)
