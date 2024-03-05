from django.contrib import admin

from geotrek.common.mixins.actions import MergeActionMixin
from .models import PhysicalType, LandType, CirculationType, AuthorizationType


@admin.register(PhysicalType)
class PhysicalTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'structure')
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"


@admin.register(LandType)
class LandTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'right_of_way', )
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"


@admin.register(CirculationType)
class CirculationTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'structure', )
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"


@admin.register(AuthorizationType)
class AuthorizationTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'structure', )
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"
