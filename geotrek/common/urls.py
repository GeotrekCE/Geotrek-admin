from django.urls import path, converters, register_converter
from mapentity.registry import MapEntityOptions

from .views import (HDViewPointCreate, HDViewPointDetail, JSSettings, admin_check_extents, DocumentPublic, DocumentBookletPublic, import_view, import_update_json,
                    ThemeViewSet, MarkupPublic, sync_view, sync_update_json, SyncRandoRedirect)


class LangConverter(converters.StringConverter):
    regex = '[a-z]{2}'


register_converter(LangConverter, 'lang')

app_name = 'common'
urlpatterns = [
    path('api/settings.json', JSSettings.as_view(), name='settings_json'),
    path('tools/extents/', admin_check_extents, name='check_extents'),
    path('commands/import-update.json', import_update_json, name='import_update_json'),
    path('commands/import', import_view, name='import_dataset'),
    path('commands/sync', SyncRandoRedirect.as_view(), name='sync_randos'),
    path('commands/syncview', sync_view, name='sync_randos_view'),
    path('commands/statesync/', sync_update_json, name='sync_randos_state'),
    path('api/<lang:lang>/themes.json', ThemeViewSet.as_view({'get': 'list'}), name="themes_json"),
    path('hdviewpoint/add', HDViewPointCreate.as_view(), name="hdviewpoint_add"),
    path('hdviewpoint/<int:pk>', HDViewPointDetail.as_view(), name="hdviewpoint_detail"),
]


class PublishableEntityOptions(MapEntityOptions):
    document_public_view = DocumentPublic
    document_public_booklet_view = DocumentBookletPublic
    markup_public_view = MarkupPublic

    def scan_views(self, *args, **kwargs):
        """ Adds the URLs of all views provided by ``PublishableMixin`` models.
        """
        views = super().scan_views(*args, **kwargs)
        publishable_views = [
            path('api/<lang:lang>/{name}s/<int:pk>/<slug:slug>_booklet.pdf'.format(name=self.modelname),
                 self.document_public_booklet_view.as_view(model=self.model),
                 name="%s_booklet_printable" % self.modelname),
            path('api/<lang:lang>/{name}s/<int:pk>/<slug:slug>.pdf'.format(name=self.modelname),
                 self.document_public_view.as_view(model=self.model),
                 name="%s_printable" % self.modelname),
            path('api/<lang:lang>/{name}s/<int:pk>/<slug:slug>.html'.format(name=self.modelname),
                 self.markup_public_view.as_view(model=self.model)),
        ]
        return publishable_views + views
