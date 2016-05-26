from django.conf.urls import patterns, url
from mapentity.registry import MapEntityOptions

from .views import (JSSettings, admin_check_extents, DocumentPublic, import_view, import_update_json,
                    ThemeViewSet)


urlpatterns = patterns(
    '',
    url(r'^api/settings.json', JSSettings.as_view(), name='settings_json'),
    url(r'^tools/extents/', admin_check_extents, name='check_extents'),
    url(r'^commands/import-update.json$', import_update_json, name='import_update_json'),
    url(r'^commands/import$', import_view, name='import_dataset'),
    url(r'^api/(?P<lang>\w\w)/themes.json$', ThemeViewSet.as_view({'get': 'list'}), name="themes_json"),
)


class PublishableEntityOptions(MapEntityOptions):
    document_public_view = DocumentPublic

    def scan_views(self, *args, **kwargs):
        """ Adds the URLs of all views provided by ``PublishableMixin`` models.
        """
        views = super(PublishableEntityOptions, self).scan_views(*args, **kwargs)
        publishable_views = patterns(
            '',
            url(r'^api/(?P<lang>\w+)/{name}s/(?P<pk>\d+)/(?P<slug>[-_\w]+).pdf$'.format(name=self.modelname),
                self.document_public_view.as_view(model=self.model),
                name="%s_printable" % self.modelname),
        )
        return publishable_views + views
