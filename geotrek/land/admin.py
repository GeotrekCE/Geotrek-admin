# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import PhysicalType, LandType, RestrictedAreaType


class PhysicalTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class LandTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'right_of_way', )
    search_fields = ('name',)


admin.site.register(PhysicalType, PhysicalTypeAdmin)
admin.site.register(LandType, LandTypeAdmin)
admin.site.register(RestrictedAreaType)
