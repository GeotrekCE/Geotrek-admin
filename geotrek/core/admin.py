from django.contrib import admin

from geotrek.core.models import (PathSource, Stake, Usage, Network, Comfort)
from geotrek.common.mixins import MergeActionMixin


class PathSourceAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('source', 'structure')
    search_fields = ('source', 'structure')
    list_filter = ('structure',)
    merge_field = "source"


class StakeAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('stake', 'structure')
    search_fields = ('stake', 'structure')
    list_filter = ('structure',)
    merge_field = "stake"


class UsageAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('usage', 'structure')
    search_fields = ('usage', 'structure')
    list_filter = ('structure',)
    merge_field = "usage"


class NetworkAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('network', 'structure')
    search_fields = ('network', 'structure')
    list_filter = ('structure',)
    merge_field = "network"


class ComfortAdmin(MergeActionMixin, admin.ModelAdmin):
    list_display = ('comfort', 'structure')
    search_fields = ('comfort', 'structure')
    list_filter = ('structure',)
    merge_field = "comfort"


admin.site.register(PathSource, PathSourceAdmin)
admin.site.register(Stake, StakeAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Comfort, ComfortAdmin)
