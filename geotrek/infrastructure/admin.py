# -*- encoding: UTF-8 -*-

from django.contrib import admin

from geotrek.infrastructure.models import InfrastructureType, InfrastructureCondition


class InfrastructureTypeAdmin(admin.ModelAdmin):
    search_fields = ('label', 'structure')

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super(InfrastructureTypeAdmin, self).get_queryset(request)
        if not request.user.has_perm('authent.can_bypass_structure'):
            qs = qs.filter(structure=request.user.profile.structure)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'structure':
            if not request.user.has_perm('authent.can_bypass_structure'):
                return None
            kwargs['initial'] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('authent.can_bypass_structure'):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ('label', 'type')
        return ('label', 'type', 'structure')

    def get_list_filter(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ('type', )
        return ('type', 'structure')


class InfrastructureConditionAdmin(admin.ModelAdmin):
    search_fields = ('label', 'structure')

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super(InfrastructureConditionAdmin, self).get_queryset(request)
        if not request.user.has_perm('authent.can_bypass_structure'):
            qs = qs.filter(structure=request.user.profile.structure)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'structure':
            if not request.user.has_perm('authent.can_bypass_structure'):
                return None
            kwargs['initial'] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('authent.can_bypass_structure'):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ('label', )
        return ('label', 'structure')

    def get_list_filter(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ()
        return ('structure',)


admin.site.register(InfrastructureType, InfrastructureTypeAdmin)
admin.site.register(InfrastructureCondition, InfrastructureConditionAdmin)
