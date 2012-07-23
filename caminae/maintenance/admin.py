# -*- coding: utf-8 -*-


from django.contrib import admin

from caminae.maintenance.models import (
        Contractor, InterventionStatus, InterventionTypology, InterventionDisorder
)

class InterventionStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)
    search_fields = ('status', )


class InterventionTypologyAdmin(admin.ModelAdmin):
    list_display = ('typology',)
    search_fields = ('typology',)


class InterventionDisorderAdmin(admin.ModelAdmin):
    list_display = ('disorder',)
    search_fields = ('disorder',)


admin.site.register(Contractor)
admin.site.register(InterventionStatus, InterventionStatusAdmin)
admin.site.register(InterventionTypology, InterventionTypologyAdmin)
admin.site.register(InterventionDisorder, InterventionDisorderAdmin)

