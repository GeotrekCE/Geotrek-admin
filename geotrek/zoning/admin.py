from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext as _
from leaflet.admin import LeafletGeoAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

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


class VigilanceAreaTypeAdmin(TreeAdmin, TabbedTranslationAdmin):
    search_fields = ("name", "code")
    list_display = ("name", "code", "pictogram_img")
    form = movenodeform_factory(zoning_models.VigilanceAreaType)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["code"].help_text = _(
            "If left empty, the code of the nearest parent that has one is used."
        )
        form.base_fields["pictogram"].help_text = _(
            "If left empty, the pictogram of the nearest parent that has one is used."
        )
        return form


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

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs["help_texts"] = {
            "level": _("Level 1 is considered the highest vigilance level."),
        }
        return super().get_form(request, obj=obj, change=change, **kwargs)


admin.site.register(zoning_models.RestrictedAreaType, RestrictedAreaTypeAdmin)
admin.site.register(zoning_models.RestrictedArea, RestrictedAreaAdmin)
admin.site.register(zoning_models.City, CityAdmin)
admin.site.register(zoning_models.District, DistrictAdmin)
admin.site.register(zoning_models.VigilanceAreaType, VigilanceAreaTypeAdmin)
admin.site.register(zoning_models.VigilanceLevel, VigilanceLevelAdmin)
