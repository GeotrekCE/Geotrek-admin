# -*- encoding: UTF-8 -*-

from django.contrib import admin

from geotrek.signage.models import SignageType


class SignageTypeAdmin(admin.ModelAdmin):
    search_fields = ('label', 'structure')

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super(SignageTypeAdmin, self).get_queryset(request)
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
            return ('label', 'type', 'pictogram_img')
        return ('label', 'structure', 'pictogram_img')

    def get_list_filter(self, request):
        if not request.user.has_perm('authent.can_bypass_structure'):
            return ()
        return ('structure', )


admin.site.register(SignageType, SignageTypeAdmin)
