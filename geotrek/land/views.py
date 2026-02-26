from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from mapentity import views as me_views

from geotrek.altimetry.models import AltimetryMixin
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.core.views import CreateFromTopologyMixin

from . import filters, forms, layers, models, serializers


class PhysicalEdgeList(
    CustomColumnsMixin, CreateFromTopologyMixin, me_views.MapEntityList
):
    queryset = models.PhysicalEdge.objects.existing()
    mandatory_columns = ["id", "physical_type"]
    default_extra_columns = ["length", "length_2d"]


class PhysicalEdgeFilter(me_views.MapEntityFilter):
    model = models.PhysicalEdge
    filterset_class = filters.PhysicalEdgeFilterSet


class PhysicalEdgeFormatList(me_views.MapEntityFormat, PhysicalEdgeList):
    filterset_class = filters.PhysicalEdgeFilterSet
    mandatory_columns = ["id", "physical_type"]
    default_extra_columns = [
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        *AltimetryMixin.COLUMNS,
    ]


class PhysicalEdgeDetail(me_views.MapEntityDetail):
    queryset = models.PhysicalEdge.objects.existing()


class PhysicalEdgeDocument(me_views.MapEntityDocument):
    model = models.PhysicalEdge


class PhysicalEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.PhysicalEdge
    form_class = forms.PhysicalEdgeForm


class PhysicalEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.PhysicalEdge.objects.existing()
    form_class = forms.PhysicalEdgeForm


class PhysicalEdgeDelete(me_views.MapEntityDelete):
    model = models.PhysicalEdge


class PhysicalEdgeViewSet(GeotrekMapentityViewSet):
    model = models.PhysicalEdge
    serializer_class = serializers.PhysicalEdgeSerializer
    geojson_serializer_class = serializers.PhysicalEdgeGeojsonSerializer
    filterset_class = filters.PhysicalEdgeFilterSet
    mapentity_list_class = PhysicalEdgeList

    def get_layer_classes(self):
        return [layers.PhysicalEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("physical_type")

        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "physical_type")
            return qs

        return qs.defer("geom", "geom_3d")


class LandEdgeList(CustomColumnsMixin, me_views.MapEntityList):
    queryset = models.LandEdge.objects.existing()
    mandatory_columns = ["id", "land_type"]
    default_extra_columns = ["length", "length_2d"]


class LandEdgeFilter(me_views.MapEntityFilter):
    model = models.LandEdge
    filterset_class = filters.LandEdgeFilterSet


class LandEdgeFormatList(me_views.MapEntityFormat, LandEdgeList):
    filterset_class = filters.LandEdgeFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "land_type",
        "owner",
        "agreement",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        "length_2d",
        *AltimetryMixin.COLUMNS,
    ]


class LandEdgeDetail(me_views.MapEntityDetail):
    queryset = models.LandEdge.objects.existing()


class LandEdgeDocument(me_views.MapEntityDocument):
    model = models.LandEdge


class LandEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.LandEdge
    form_class = forms.LandEdgeForm


class LandEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.LandEdge.objects.existing()
    form_class = forms.LandEdgeForm


class LandEdgeDelete(me_views.MapEntityDelete):
    model = models.LandEdge


class LandEdgeViewSet(GeotrekMapentityViewSet):
    model = models.LandEdge
    serializer_class = serializers.LandEdgeSerializer
    geojson_serializer_class = serializers.LandEdgeGeojsonSerializer
    filterset_class = filters.LandEdgeFilterSet
    mapentity_list_class = LandEdgeList

    def get_layer_classes(self):
        return [layers.LandEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("land_type")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "land_type")
            return qs
        return qs.defer("geom", "geom_3d")


class CirculationEdgeList(CustomColumnsMixin, me_views.MapEntityList):
    queryset = models.CirculationEdge.objects.existing()
    mandatory_columns = ["id", "circulation_type", "authorization_type"]
    default_extra_columns = ["length", "length_2d"]


class CirculationEdgeFilter(me_views.MapEntityFilter):
    model = models.CirculationEdge
    filterset_class = filters.CirculationEdgeFilterSet


class CirculationEdgeFormatList(me_views.MapEntityFormat, CirculationEdgeList):
    filterset_class = filters.CirculationEdgeFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "circulation_type",
        "authorization_type",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        "length_2d",
        *AltimetryMixin.COLUMNS,
    ]


class CirculationEdgeDetail(me_views.MapEntityDetail):
    queryset = models.CirculationEdge.objects.existing()


class CirculationEdgeDocument(me_views.MapEntityDocument):
    model = models.CirculationEdge


class CirculationEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.CirculationEdge
    form_class = forms.CirculationEdgeForm


class CirculationEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.CirculationEdge.objects.existing()
    form_class = forms.CirculationEdgeForm


class CirculationEdgeDelete(me_views.MapEntityDelete):
    model = models.CirculationEdge


class CirculationEdgeViewSet(GeotrekMapentityViewSet):
    model = models.CirculationEdge
    serializer_class = serializers.CirculationEdgeSerializer
    geojson_serializer_class = serializers.CirculationEdgeGeojsonSerializer
    filterset_class = filters.CirculationEdgeFilterSet
    mapentity_list_class = CirculationEdgeList

    def get_layer_classes(self):
        return [layers.CirculationEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("circulation_type")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "circulation_type")
            return qs
        return qs.defer("geom", "geom_3d")


class CompetenceEdgeList(CustomColumnsMixin, me_views.MapEntityList):
    queryset = models.CompetenceEdge.objects.existing()
    mandatory_columns = ["id", "organization"]
    default_extra_columns = ["length", "length_2d"]


class CompetenceEdgeFilter(me_views.MapEntityFilter):
    model = models.CompetenceEdge
    filterset_class = filters.CompetenceEdgeFilterSet


class CompetenceEdgeFormatList(me_views.MapEntityFormat, CompetenceEdgeList):
    filterset_class = filters.CompetenceEdgeFilterSet
    mandatory_columns = ["id", "organization"]
    default_extra_columns = [
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        "length_2d",
        *AltimetryMixin.COLUMNS,
    ]


class CompetenceEdgeDetail(me_views.MapEntityDetail):
    queryset = models.CompetenceEdge.objects.existing()


class CompetenceEdgeDocument(me_views.MapEntityDocument):
    model = models.CompetenceEdge


class CompetenceEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.CompetenceEdge
    form_class = forms.CompetenceEdgeForm


class CompetenceEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.CompetenceEdge.objects.existing()
    form_class = forms.CompetenceEdgeForm


class CompetenceEdgeDelete(me_views.MapEntityDelete):
    model = models.CompetenceEdge


class CompetenceEdgeViewSet(GeotrekMapentityViewSet):
    model = models.CompetenceEdge
    serializer_class = serializers.CompetenceEdgeSerializer
    geojson_serializer_class = serializers.CompetenceEdgeGeojsonSerializer
    filterset_class = filters.CompetenceEdgeFilterSet
    mapentity_list_class = CompetenceEdgeList

    def get_layer_classes(self):
        return [layers.CompetenceEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("organization")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "organization")
            return qs
        return qs.defer("geom", "geom_3d")


class WorkManagementEdgeList(CustomColumnsMixin, me_views.MapEntityList):
    queryset = models.WorkManagementEdge.objects.existing()
    mandatory_columns = ["id", "organization"]
    default_extra_columns = ["length", "length_2d"]


class WorkManagementEdgeFilter(me_views.MapEntityFilter):
    model = models.WorkManagementEdge
    filterset_class = filters.WorkManagementEdgeFilterSet


class WorkManagementEdgeFormatList(me_views.MapEntityFormat, WorkManagementEdgeList):
    filterset_class = filters.WorkManagementEdgeFilterSet
    mandatory_columns = ["id", "organization"]
    default_extra_columns = [
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        "length_2d",
        *AltimetryMixin.COLUMNS,
    ]


class WorkManagementEdgeDetail(me_views.MapEntityDetail):
    queryset = models.WorkManagementEdge.objects.existing()


class WorkManagementEdgeDocument(me_views.MapEntityDocument):
    model = models.WorkManagementEdge


class WorkManagementEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.WorkManagementEdge
    form_class = forms.WorkManagementEdgeForm


class WorkManagementEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.WorkManagementEdge.objects.existing()
    form_class = forms.WorkManagementEdgeForm


class WorkManagementEdgeDelete(me_views.MapEntityDelete):
    model = models.WorkManagementEdge


class WorkManagementEdgeViewSet(GeotrekMapentityViewSet):
    model = models.WorkManagementEdge
    serializer_class = serializers.WorkManagementEdgeSerializer
    geojson_serializer_class = serializers.WorkManagementEdgeGeojsonSerializer
    filterset_class = filters.WorkManagementEdgeFilterSet
    mapentity_list_class = WorkManagementEdgeList

    def get_layer_classes(self):
        return [layers.WorkManagementEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("organization")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "organization")
            return qs
        return qs.defer("geom", "geom_3d")


class SignageManagementEdgeList(CustomColumnsMixin, me_views.MapEntityList):
    queryset = models.SignageManagementEdge.objects.existing()
    mandatory_columns = ["id", "organization"]
    default_extra_columns = ["length", "length_2d"]


class SignageManagementEdgeFilter(me_views.MapEntityFilter):
    model = models.SignageManagementEdge
    filterset_class = filters.SignageManagementEdgeFilterSet


class SignageManagementEdgeFormatList(
    me_views.MapEntityFormat, SignageManagementEdgeList
):
    filterset_class = filters.SignageManagementEdgeFilterSet
    mandatory_columns = ["id", "organization"]
    default_extra_columns = [
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        "length_2d",
        *AltimetryMixin.COLUMNS,
    ]


class SignageManagementEdgeDetail(me_views.MapEntityDetail):
    queryset = models.SignageManagementEdge.objects.existing()


class SignageManagementEdgeDocument(me_views.MapEntityDocument):
    model = models.SignageManagementEdge


class SignageManagementEdgeCreate(CreateFromTopologyMixin, me_views.MapEntityCreate):
    model = models.SignageManagementEdge
    form_class = forms.SignageManagementEdgeForm


class SignageManagementEdgeUpdate(me_views.MapEntityUpdate):
    queryset = models.SignageManagementEdge.objects.existing()
    form_class = forms.SignageManagementEdgeForm


class SignageManagementEdgeDelete(me_views.MapEntityDelete):
    model = models.SignageManagementEdge


class SignageManagementEdgeViewSet(GeotrekMapentityViewSet):
    model = models.SignageManagementEdge
    serializer_class = serializers.SignageManagementEdgeSerializer
    geojson_serializer_class = serializers.SignageManagementEdgeGeojsonSerializer
    filterset_class = filters.SignageManagementEdgeFilterSet
    mapentity_list_class = SignageManagementEdgeList

    def get_layer_classes(self):
        return [layers.SignageManagementEdgeVectorLayer]

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("organization")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "organization")
            return qs
        return qs.defer("geom", "geom_3d")
