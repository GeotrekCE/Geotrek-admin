from django.contrib import admin
from django.db.models import Q

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.signage.models import (
    BladeCondition,
    BladeType,
    Color,
    Direction,
    LinePictogram,
    Sealing,
    SignageCondition,
    SignageType,
)


@admin.register(Color)
class ColorBladeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label",)
    merge_field = "label"


@admin.register(Direction)
class DirectionBladeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label",)
    merge_field = "label"


@admin.register(LinePictogram)
class LinePictogramAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label",)
    merge_field = "label"
    list_display = ("label", "pictogram_img", "code")


@admin.register(Sealing)
class SealingAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label",)
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm("authent.can_bypass_structure"):
            qs = qs.filter(structure=request.user.profile.structure)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "structure":
            if not request.user.has_perm("authent.can_bypass_structure"):
                return None
            kwargs["initial"] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm("authent.can_bypass_structure"):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ("label",)
        return ("label", "structure")

    def get_list_filter(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ()
        return ("structure",)


@admin.register(BladeType)
class BladeTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label", "structure")
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm("authent.can_bypass_structure"):
            qs = qs.filter(structure=request.user.profile.structure)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "structure":
            if not request.user.has_perm("authent.can_bypass_structure"):
                return None
            kwargs["initial"] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm("authent.can_bypass_structure"):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ("label",)
        return ("label", "structure")

    def get_list_filter(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ()
        return ("structure",)


@admin.register(SignageType)
class SignageTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label", "structure")
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm("authent.can_bypass_structure"):
            qs = qs.filter(structure=request.user.profile.structure)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "structure":
            if not request.user.has_perm("authent.can_bypass_structure"):
                return None
            kwargs["initial"] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm("authent.can_bypass_structure"):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ("label", "pictogram_img")
        return ("label", "structure", "pictogram_img")

    def get_list_filter(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ()
        return ("structure",)


@admin.register(BladeCondition, SignageCondition)
class ModelConditionAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("label", "structure__name")
    merge_field = "label"

    def get_queryset(self, request):
        """
        filter objects by structure
        """
        qs = super().get_queryset(request)
        if not request.user.has_perm("authent.can_bypass_structure"):
            qs = qs.filter(
                Q(structure=request.user.profile.structure) | Q(structure=None)
            )
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "structure":
            if not request.user.has_perm("authent.can_bypass_structure"):
                return None
            kwargs["initial"] = request.user.profile.structure
            return db_field.formfield(**kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm("authent.can_bypass_structure"):
            obj.structure = request.user.profile.structure
        obj.save()

    def get_list_display(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ("label",)
        return ("label", "structure")

    def get_list_filter(self, request):
        if not request.user.has_perm("authent.can_bypass_structure"):
            return ()
        return ("structure",)
