from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(PathManagerModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
