from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin

from geotrek.zoning import models as zoning_models


class RestrictedAreaTypeAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class CityAdmin(LeafletGeoAdmin):
    search_fields = ('code', 'name')
    list_display = ('name', 'code',)


class RestrictedAreaAdmin(LeafletGeoAdmin):
    search_fields = ('name',)
    list_display = ('name', 'area_type')
    list_filter = ('area_type',)


class DistrictAdmin(LeafletGeoAdmin):
    search_fields = ('name',)
    list_display = ('name',)


admin.site.register(zoning_models.RestrictedAreaType, RestrictedAreaTypeAdmin)
admin.site.register(zoning_models.RestrictedArea, RestrictedAreaAdmin)
admin.site.register(zoning_models.City, CityAdmin)
admin.site.register(zoning_models.District, DistrictAdmin)
