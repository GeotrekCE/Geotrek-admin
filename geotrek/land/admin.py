from django.contrib import admin

from geotrek.common.mixins import MergeActionMixin
from .models import PhysicalType, LandType


class PhysicalTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'structure')
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"


class LandTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('name', 'right_of_way', )
    search_fields = ('name', 'structure')
    list_filter = ('structure',)
    merge_field = "name"


admin.site.register(PhysicalType, PhysicalTypeAdmin)
admin.site.register(LandType, LandTypeAdmin)
