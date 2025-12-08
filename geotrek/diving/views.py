from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from mapentity.views import (
    MapEntityCreate,
    MapEntityDelete,
    MapEntityDetail,
    MapEntityDocument,
    MapEntityFilter,
    MapEntityFormat,
    MapEntityList,
    MapEntityMapImage,
    MapEntityUpdate,
)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.views import DocumentBookletPublic, DocumentPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.trekking.views import FlattenPicturesMixin

from .filters import DiveFilterSet
from .forms import DiveForm
from .models import Dive
from .serializers import DiveGeojsonSerializer, DiveSerializer


class DiveList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    queryset = Dive.objects.existing()
    mandatory_columns = ["id", "name"]
    default_extra_columns = ["levels", "thumbnail"]
    unorderable_columns = ["thumbnail"]
    searchable_columns = ["id", "name"]


class DiveFilter(MapEntityFilter):
    model = Dive
    filterset_class = DiveFilterSet


class DiveFormatList(MapEntityFormat, DiveList):
    filterset_class = DiveFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "eid",
        "structure",
        "name",
        "departure",
        "description",
        "description_teaser",
        "advice",
        "difficulty",
        "levels",
        "themes",
        "practice",
        "disabled_sport",
        "published",
        "publication_date",
        "date_insert",
        "date_update",
        "areas",
        "source",
        "portal",
        "review",
    ]


class DiveDetail(CompletenessMixin, MapEntityDetail):
    queryset = Dive.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        return context


class DiveMapImage(MapEntityMapImage):
    queryset = Dive.objects.existing()


class DiveDocument(MapEntityDocument):
    queryset = Dive.objects.existing()


class DiveDocumentPublicMixin:
    queryset = Dive.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dive = self.get_object()
        context["headerimage_ratio"] = settings.EXPORT_HEADER_IMAGE_SIZE["dive"]
        context["object"] = context["dive"] = dive
        return context


class DiveDocumentPublic(DiveDocumentPublicMixin, DocumentPublic):
    pass


class DiveDocumentBookletPublic(DiveDocumentPublicMixin, DocumentBookletPublic):
    pass


class DiveMarkupPublic(DiveDocumentPublicMixin, MarkupPublic):
    pass


class DiveCreate(MapEntityCreate):
    model = Dive
    form_class = DiveForm


class DiveUpdate(MapEntityUpdate):
    queryset = Dive.objects.existing()
    form_class = DiveForm

    @same_structure_required("diving:dive_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DiveDelete(MapEntityDelete):
    model = Dive

    @same_structure_required("diving:dive_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DiveViewSet(GeotrekMapentityViewSet):
    model = Dive
    serializer_class = DiveSerializer
    geojson_serializer_class = DiveGeojsonSerializer
    filterset_class = DiveFilterSet
    mapentity_list_class = DiveList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "name", "published")

        return qs
