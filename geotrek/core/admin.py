from django.contrib import admin

from geotrek.authent.admin import PathManagerModelAdmin
from geotrek.core.models import (Datasource, Stake, Usage, Network, Trail,
                                 Comfort,)


class DatasourceAdmin(PathManagerModelAdmin):
    list_display = ('source', 'structure')
    search_fields = ('source', 'structure')
    list_filter = ('structure',)


class StakeAdmin(PathManagerModelAdmin):
    list_display = ('stake', 'structure')
    search_fields = ('stake', 'structure')
    list_filter = ('structure',)


class UsageAdmin(PathManagerModelAdmin):
    list_display = ('usage', 'structure')
    search_fields = ('usage', 'structure')
    list_filter = ('structure',)


class NetworkAdmin(PathManagerModelAdmin):
    list_display = ('network', 'structure')
    search_fields = ('network', 'structure')
    list_filter = ('structure',)


class TrailAdmin(PathManagerModelAdmin):
    list_display = ('name', 'structure')
    search_fields = ('name', 'structure')
    list_filter = ('structure',)


class ComfortAdmin(PathManagerModelAdmin):
    list_display = ('comfort', 'structure')
    search_fields = ('comfort', 'structure')
    list_filter = ('structure',)


admin.site.register(Datasource, DatasourceAdmin)
admin.site.register(Stake, StakeAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Trail, TrailAdmin)
admin.site.register(Comfort, ComfortAdmin)
