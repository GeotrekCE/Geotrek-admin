from django.contrib import admin
from django.conf import settings

from geotrek.flatpages import models as flatpages_models
from geotrek.flatpages.views import FlatPageCreate, FlatPageUpdate


class FlatPagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'publication_date', 'target')
    search_fields = ('title', 'content')

    def add_view(self, request, form_url='', extra_context=None):
        return FlatPageCreate.as_view()(request)

    def change_view(self, request, pk, form_url='', extra_context=None):
        return FlatPageUpdate.as_view()(request, pk=pk)


if settings.FLATPAGES_ENABLED:
    admin.site.register(flatpages_models.FlatPage, FlatPagesAdmin)
