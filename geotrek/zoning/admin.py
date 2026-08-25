from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from leaflet.admin import LeafletGeoAdmin

if "modeltranslation" in settings.INSTALLED_APPS:
    from modeltranslation.admin import TabbedTranslationAdmin
else:
    from django.contrib.admin import ModelAdmin as TabbedTranslationAdmin

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.zoning import models as zoning_models


@admin.action(description=_("Publish (visible on Geotrek-rando)"))
def publish(modeladmin, request, queryset):
    queryset.update(published=True)


@admin.action(description=_("Unpublish (hidden on Geotrek-rando)"))
def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)


class RestrictedAreaTypeAdmin(MergeActionMixin, admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)
    merge_field = "name"


class CityAdmin(LeafletGeoAdmin):
    search_fields = ("code", "name")
    list_display = ("name", "code", "published")
    list_filter = ("published",)
    actions = (publish, unpublish)


class RestrictedAreaAdmin(LeafletGeoAdmin):
    search_fields = ("name",)
    list_display = ("name", "area_type", "published")
    list_filter = ("area_type", "published")
    actions = (publish, unpublish)


class DistrictAdmin(LeafletGeoAdmin):
    search_fields = ("name",)
    list_display = ("name", "published")
    list_filter = ("published",)
    actions = (publish, unpublish)


class VigilanceAreaTypeAdmin(TabbedTranslationAdmin):
    search_fields = ("name", "description")
    list_display = ("name", "pictogram_img")


class VigilanceLevelAdmin(TabbedTranslationAdmin):
    search_fields = ("name",)
    list_display = ("name", "color_markup", "pictogram_img")

    @admin.display(description=_("Color"))
    def color_markup(self, obj):
        if not obj.color:
            return ""
        return format_html(
            '<span style="color: {code};">⬤</span> {code}', code=obj.color
        )


admin.site.register(zoning_models.RestrictedAreaType, RestrictedAreaTypeAdmin)
admin.site.register(zoning_models.RestrictedArea, RestrictedAreaAdmin)
admin.site.register(zoning_models.City, CityAdmin)
admin.site.register(zoning_models.District, DistrictAdmin)
admin.site.register(zoning_models.VigilanceAreaType, VigilanceAreaTypeAdmin)
admin.site.register(zoning_models.VigilanceLevel, VigilanceLevelAdmin)
