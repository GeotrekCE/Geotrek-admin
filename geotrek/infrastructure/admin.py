from django.contrib import admin

from geotrek.infrastructure.models import InfrastructureType, InfrastructureState


class InfrastructureTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'type', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('type', 'structure',)


class InfrastructureStateAdmin(admin.ModelAdmin):
    list_display = ('label', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('structure',)


admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
admin.site.register(InfrastructureState, InfrastructureStateAdmin)
