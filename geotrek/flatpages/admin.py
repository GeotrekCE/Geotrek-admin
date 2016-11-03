from django.contrib import admin
from django.conf import settings
from django.utils.translation import ugettext as _

from geotrek.flatpages import models as flatpages_models
from geotrek.flatpages.views import FlatPageCreate, FlatPageUpdate


class FlatPagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'publication_date', 'order', 'portals', 'target')
    list_filter = ('published', 'target')
    search_fields = ('title', 'content')

    def add_view(self, request, form_url='', extra_context=None):
        return FlatPageCreate.as_view()(request)

    def change_view(self, request, pk, form_url='', extra_context=None):
        return FlatPageUpdate.as_view()(request, pk=pk)

    def portals(self, obj):
        return ', '.join([portal.name for portal in obj.portal.all()])
    portals.short_description = _("Portals")


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
