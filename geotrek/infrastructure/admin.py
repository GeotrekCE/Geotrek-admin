from django.contrib import admin
from django.db.models import Q

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.infrastructure.models import InfrastructureMaintenanceDifficultyLevel, InfrastructureType, InfrastructureCondition, InfrastructureUsageDifficultyLevel


@admin.register(InfrastructureType)
class InfrastructureTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ('label', 'structure__name')
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm('authent.can_bypass_structure'):
            qs = qs.filter(Q(structure=request.user.profile.structure) | Q(structure=None))
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
            return ('label', 'type', 'pictogram_img')
        return ('label', 'type', 'structure', 'pictogram_img')

    def get_list_filter(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ('type', )
        return ('type', 'structure')


@admin.register(InfrastructureCondition, InfrastructureMaintenanceDifficultyLevel, InfrastructureUsageDifficultyLevel)
class InfrastructureSimpleFieldAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ('label', 'structure__name')
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm('authent.can_bypass_structure'):
            qs = qs.filter(Q(structure=request.user.profile.structure) | Q(structure=None))
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
