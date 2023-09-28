from django.conf import settings
from django.urls import path, converters, register_converter, re_path
from mapentity.registry import MapEntityOptions, registry
from mapentity.urls import _MEDIA_URL
from rest_framework.routers import DefaultRouter

from .models import HDViewPoint
from . import views


class LangConverter(converters.StringConverter):
    regex = "[a-z]{2}"


register_converter(LangConverter, "lang")

app_name = "common"


urlpatterns = [
    path("api/settings.json", views.JSSettings.as_view(), name="settings_json"),
    path("tools/extents/", views.CheckExtentsView.as_view(), name="check_extents"),
    path(
        "commands/import-update.json",
        views.import_update_json,
        name="import_update_json",
    ),
    path("commands/import", views.import_view, name="import_dataset"),
    path("commands/sync", views.SyncRandoRedirect.as_view(), name="sync_randos"),
    path("commands/syncview", views.sync_view, name="sync_randos_view"),
    path("commands/statesync/", views.sync_update_json, name="sync_randos_state"),
    path(
        "api/<lang:lang>/themes.json",
        views.ThemeViewSet.as_view({"get": "list"}),
        name="themes_json",
    ),
    path(
        "hdviewpoint/annotate/<int:pk>",
        views.HDViewPointAnnotate.as_view(),
        name="hdviewpoint_annotate",
    ),
    path(
        "add-accessibility-for/<str:app_label>/<str:model_name>/<int:pk>/",
        views.add_attachment_accessibility,
        name="add_attachment_accessibility",
    ),
    path(
        "update-accessibility/<int:attachment_pk>/",
        views.update_attachment_accessibility,
        name="update_attachment_accessibility",
    ),
    path(
        "delete-accessibility/<int:attachment_pk>/",
        views.delete_attachment_accessibility,
        name="delete_attachment_accessibility",
    ),
]

if settings.DEBUG or settings.MAPENTITY_CONFIG["SENDFILE_HTTP_HEADER"]:
    urlpatterns += [
        re_path(
            r"^%s/(?P<path>attachments_accessibility/.*)$" % _MEDIA_URL,
            views.ServeAttachmentAccessibility.as_view(),
        ),
    ]

rest_router = DefaultRouter(trailing_slash=False)
rest_router.register(r"api/hdviewpoint/drf/hdviewpoints", views.TiledHDViewPointViewSet)
urlpatterns += registry.register(HDViewPoint, menu=False)
urlpatterns += rest_router.urls


class PublishableEntityOptions(MapEntityOptions):
    document_public_view = views.DocumentPublic
    document_public_booklet_view = views.DocumentBookletPublic
    markup_public_view = views.MarkupPublic

    def scan_views(self, *args, **kwargs):
        """Adds the URLs of all views provided by ``PublishableMixin`` models."""
        mapentity_views = super().scan_views()
        publishable_views = [
            path(
                "api/<lang:lang>/{name}s/<int:pk>/<slug:slug>_booklet.pdf".format(
                    name=self.modelname
                ),
                self.document_public_booklet_view.as_view(model=self.model),
                name="%s_booklet_printable" % self.modelname,
            ),
            path(
                "api/<lang:lang>/{name}s/<int:pk>/<slug:slug>.pdf".format(
                    name=self.modelname
                ),
                self.document_public_view.as_view(model=self.model),
                name="%s_printable" % self.modelname,
            ),
            path(
                "api/<lang:lang>/{name}s/<int:pk>/<slug:slug>.html".format(
                    name=self.modelname
                ),
                self.markup_public_view.as_view(model=self.model),
            ),
        ]
        return publishable_views + mapentity_views
