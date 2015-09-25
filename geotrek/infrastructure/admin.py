# -*- encoding: UTF-8 -*-

from django.contrib import admin

from geotrek.authent.models import Structure
from geotrek.infrastructure.models import InfrastructureType, InfrastructureCondition


class InfrastructureTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'type', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('type', 'structure',)


class InfrastructureConditionAdmin(admin.ModelAdmin):
    list_display = ('label', 'structure')
    search_fields = ('label', 'structure')
    list_filter = ('structure',)

    def get_form(self, request, obj=None, **kwargs):
        """
        custom admin form generation
        """
        form = super(InfrastructureConditionAdmin, self).get_form(request, obj, **kwargs)

        if not request.user.has_perm('infrastructure.add_infrastructurestate'):
            form.base_fields['structure'].queryset = Structure.objects.filter(pk=request.user.profile.structure_id)

        return form


admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
admin.site.register(InfrastructureCondition, InfrastructureConditionAdmin)
