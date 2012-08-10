from django.contrib import admin

from caminae.infrastructure.models import InfrastructureType


class InfrastructureTypeAdmin(admin.ModelAdmin):
    list_display = ('label',)
    search_fields = ('label',)

admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
