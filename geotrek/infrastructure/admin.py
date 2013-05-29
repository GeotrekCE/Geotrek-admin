from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(PathManagerModelAdmin):
    list_display = ('label', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('structure',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
