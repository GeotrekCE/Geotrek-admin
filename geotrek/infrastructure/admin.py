from django.contrib import admin

from geotrek.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'type', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('type', 'structure',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
