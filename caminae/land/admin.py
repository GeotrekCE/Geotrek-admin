# -*- coding: utf-8 -*-

from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from caminae.land.models import PhysicalType, LandType, RestrictedAreaType


class PhysicalTypeAdmin(TranslationAdmin):
    list_display = ('name',)


class LandTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'right_of_way', )
    search_fields = ('name',)


admin.site.register(PhysicalType, PhysicalTypeAdmin)
admin.site.register(LandType, LandTypeAdmin)
admin.site.register(RestrictedAreaType)
