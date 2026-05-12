from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins.actions import MergeActionMixin
from geotrek.core.models import (
    CertificationLabel,
    CertificationStatus,
    Comfort,
    Network,
    PathSource,
    Stake,
    TrailCategory,
    Usage,
)


@admin.register(PathSource)
class PathSourceAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("source", "structure")
    search_fields = ("source", "structure")
    list_filter = ("structure",)
    merge_field = "source"


@admin.register(Stake)
class StakeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("stake", "structure")
    search_fields = ("stake", "structure")
    list_filter = ("structure",)
    merge_field = "stake"


@admin.register(Usage)
class UsageAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("usage", "structure")
    search_fields = ("usage", "structure")
    list_filter = ("structure",)
    merge_field = "usage"


@admin.register(Network)
class NetworkAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("network", "structure")
    search_fields = ("network", "structure")
    list_filter = ("structure",)
    merge_field = "network"


@admin.register(Comfort)
class ComfortAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("comfort", "structure")
    search_fields = ("comfort", "structure")
    list_filter = ("structure",)
    merge_field = "comfort"


@admin.register(TrailCategory)
class TrailCategoryAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("label", "structure")
    search_fields = ("label", "structure")
    list_filter = ("structure",)
    merge_field = "label"


@admin.register(CertificationLabel)
class CertificationLabelAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("label", "structure")
    search_fields = ("label", "structure")
    list_filter = ("structure",)
    merge_field = "label"


@admin.register(CertificationStatus)
class CertificationStatusAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ("label", "structure")
    search_fields = ("label", "structure")
    list_filter = ("structure",)
    merge_field = "label"


admin.site.site_header = _("Geotrek configuration")
