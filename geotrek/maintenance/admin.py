from django.contrib import admin

from geotrek.maintenance.models import (
    Contractor, InterventionStatus, InterventionType, InterventionDisorder,
    ProjectType, ProjectDomain, InterventionJob,
)


class ContractorAdmin(admin.ModelAdmin):
    list_display = ('contractor', 'structure')
    search_fields = ('contractor', 'structure')
    list_filter = ('structure',)


class InterventionStatusAdmin(admin.ModelAdmin):
    list_display = ('status', 'structure')
    search_fields = ('status', 'structure')
    list_filter = ('structure',)


class InterventionTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


class InterventionDisorderAdmin(admin.ModelAdmin):
    list_display = ('disorder', 'structure')
    search_fields = ('disorder', 'structure')
    list_filter = ('structure',)


class InterventionJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'cost', 'structure')
    search_fields = ('job', 'structure')
    list_filter = ('structure',)


class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('type', 'structure')
    search_fields = ('type', 'structure')
    list_filter = ('structure',)


class ProjectDomainAdmin(admin.ModelAdmin):
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
