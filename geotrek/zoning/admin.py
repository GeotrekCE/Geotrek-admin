from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin

from geotrek.zoning import models as zoning_models


admin.site.register(zoning_models.RestrictedAreaType)
admin.site.register(zoning_models.RestrictedArea, LeafletGeoAdmin)
admin.site.register(zoning_models.City, LeafletGeoAdmin)
admin.site.register(zoning_models.District, LeafletGeoAdmin)
