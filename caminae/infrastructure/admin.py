from django.contrib import admin

from caminae.authent.admin import PathManagerModelAdmin
from caminae.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(PathManagerModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
