from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.maintenance.models import (
    Contractor, InterventionStatus, InterventionType, InterventionDisorder,
    ProjectType, ProjectDomain, InterventionJob,
)


class ContractorAdmin(PathManagerModelAdmin):
    list_display = ('contractor', 'structure')
    search_fields = ('contractor', 'structure')
    list_filter = ('structure',)


class InterventionStatusAdmin(PathManagerModelAdmin):
    list_display = ('status', 'structure')
    search_fields = ('status', 'structure')
    list_filter = ('structure',)


class InterventionTypeAdmin(PathManagerModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


class InterventionDisorderAdmin(PathManagerModelAdmin):
    list_display = ('disorder', 'structure')
    search_fields = ('disorder', 'structure')
    list_filter = ('structure',)


class InterventionJobAdmin(PathManagerModelAdmin):
    list_display = ('job', 'cost', 'structure')
    search_fields = ('job', 'structure')
    list_filter = ('structure',)


class ProjectTypeAdmin(PathManagerModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


class ProjectDomainAdmin(PathManagerModelAdmin):
    list_display = ('domain', 'structure')
    search_fields = ('domain', 'structure')
    list_filter = ('structure',)


admin.site.register(Contractor, ContractorAdmin)
admin.site.register(InterventionStatus, InterventionStatusAdmin)
admin.site.register(InterventionType, InterventionTypeAdmin)
admin.site.register(InterventionDisorder, InterventionDisorderAdmin)
admin.site.register(InterventionJob, InterventionJobAdmin)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(ProjectDomain, ProjectDomainAdmin)
