from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.maintenance.models import (
    Contractor, InterventionStatus, InterventionType, InterventionDisorder,
    ProjectType, ProjectDomain, InterventionJob,
)


class InterventionStatusAdmin(PathManagerModelAdmin):
    list_display = ('status',)
    search_fields = ('status', )


class InterventionTypeAdmin(PathManagerModelAdmin):
    list_display = ('type',)
    search_fields = ('type',)


class InterventionDisorderAdmin(PathManagerModelAdmin):
    list_display = ('disorder',)
    search_fields = ('disorder',)


class InterventionJobAdmin(PathManagerModelAdmin):
    list_display = ('job', 'cost',)
    search_fields = ('job',)


admin.site.register(Contractor, PathManagerModelAdmin)
admin.site.register(InterventionStatus, InterventionStatusAdmin)
admin.site.register(InterventionType, InterventionTypeAdmin)
admin.site.register(InterventionDisorder, InterventionDisorderAdmin)
admin.site.register(InterventionJob, InterventionJobAdmin)
admin.site.register(ProjectType, PathManagerModelAdmin)
admin.site.register(ProjectDomain, PathManagerModelAdmin)
