from django.contrib import admin

from .models import PhysicalType, LandType


class PhysicalTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'structure')
    search_fields = ('name', 'structure')
    list_filter = ('structure',)


class LandTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'right_of_way', )
    search_fields = ('name', 'structure')
    list_filter = ('structure',)


admin.site.register(PhysicalType, PhysicalTypeAdmin)
admin.site.register(LandType, LandTypeAdmin)
