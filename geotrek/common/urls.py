from django.conf import settings
from django.urls import converters, path, re_path, register_converter
from mapentity.registry import registry
from mapentity.urls import _MEDIA_URL
from rest_framework.routers import DefaultRouter

from . import entities, models, views


class LangConverter(converters.StringConverter):
    regex = "[a-z]{2}(-[a-z]{2,4})?"


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
            rf"^{_MEDIA_URL}/(?P<path>attachments_accessibility/.*)$",
            views.ServeAttachmentAccessibility.as_view(),
        ),
    ]

rest_router = DefaultRouter(trailing_slash=False)
rest_router.register(r"api/hdviewpoint/drf/hdviewpoints", views.TiledHDViewPointViewSet)

urlpatterns += registry.register(
    models.HDViewPoint, options=entities.HDViewPointEntityOptions
)
urlpatterns += rest_router.urls
