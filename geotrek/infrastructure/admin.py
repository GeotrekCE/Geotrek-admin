from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(PathManagerModelAdmin):
    list_display = ('label', 'type', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('type', 'structure',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
