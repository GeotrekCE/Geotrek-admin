# -*- encoding: UTF-8 -*-

from django.contrib import admin

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

        # if not bypass structure, hide structure field

        if not request.user.has_perm('authent.can_bypass_structure'):
            del form.base_fields['structure']

        return form

    def save_form(self, request, form, change):
        """
        custom save form
        """
        # if not bypass structure, fix user structure
        if not request.user.has_perm('authent.can_bypass_structure'):
            form.instance.structure = request.user.profile.structure

        return super(InfrastructureConditionAdmin, self).save_form(request, form, change)


admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
admin.site.register(InfrastructureCondition, InfrastructureConditionAdmin)
