from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter, PublishableEntityOptions

from . import models
from .views import (
    DiveDocumentBookletPublic,
    DiveDocumentPublic,
    DiveMapImage,
    DiveMarkupPublic,
)

register_converter(LangConverter, "lang")

app_name = "diving"

urlpatterns = [
    path(
        "image/dive-<int:pk>-<lang:lang>.png",
        DiveMapImage.as_view(),
        name="dive_map_image",
    ),
]


class DiveEntityOptions(PublishableEntityOptions):
    document_public_booklet_view = DiveDocumentBookletPublic
    document_public_view = DiveDocumentPublic
    markup_public_view = DiveMarkupPublic


urlpatterns += registry.register(
    models.Dive, DiveEntityOptions, menu=settings.DIVE_MODEL_ENABLED
)
