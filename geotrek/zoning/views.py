from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
from mapentity.decorators import view_cache_latest, view_cache_response_content
from mapentity.renderers import GeoJSONRenderer
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..common.functions import SimplifyPreserveTopology
from .models import City, District, RestrictedArea, RestrictedAreaType
from .serializers import (
    CityAutoCompleteBBoxSerializer,
    CityAutoCompleteSerializer,
    CitySerializer,
    DistrictAutoCompleteBBoxSerializer,
    DistrictAutoCompleteSerializer,
    DistrictSerializer,
    RestrictedAreaAutoCompleteBBoxSerializer,
    RestrictedAreaAutoCompleteSerializer,
    RestrictedAreaSerializer,
)


class AutocompleteMixin:
    autocomplete_search_fields = None
    serializer_autocomplete_class = None
    serializer_autocomplete_bbox_class = None

    def _get_filters(self, q):
        filters = Q()
        for field in self.autocomplete_search_fields:
            filters |= Q(**{f"{field}__icontains": q})
        return filters

    def paginate_autocomplete(self, request, queryset):
        page_number = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)
        paginated_qs = paginator.get_page(page_number)
        return paginated_qs, paginated_qs.has_next()

    @action(detail=False)
    def autocomplete_bbox(self, request, *args, **kwargs):
        qs = self.get_queryset_autocomplete_bbox()
        q = self.request.query_params.get("q")

        qs, has_more = self.paginate_autocomplete(self.request, qs.filter(self._get_filters(q)) if q else qs)

        serializer = self.serializer_autocomplete_bbox_class(qs, many=True)
        return Response({"results": serializer.data, "pagination": {"more": has_more}})


    @action(detail=False)
    def autocomplete(self, request, *args, **kwargs):
        qs = self.get_queryset_autocomplete()
        identifier = self.request.query_params.get(
            "id"
        )  # filter with id parameter is used to retrieve a known value
        if identifier:
            qs = qs.filter(id=identifier)
            instance = qs.first()
            if instance is None:
                return Response({})
            serializer = self.serializer_autocomplete_class(instance)
            data = serializer.data

        else:
            q = self.request.query_params.get("q")
            qs, has_more = self.paginate_autocomplete(request, qs.filter(self._get_filters(q)) if q else qs)

            serializer = self.serializer_autocomplete_class(qs, many=True)
            data = {"results": serializer.data, "pagination": {"more": has_more}}

        return Response(data)


class LandGeoJSONAPIViewMixin:
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [GeoJSONRenderer]

    def get_queryset(self):
        return self.model.objects.annotate(
            api_geom=Transform(
                SimplifyPreserveTopology("geom", settings.LAYER_SIMPLIFY_LAND),
                settings.API_SRID,
            )
        ).defer("geom")

    @view_cache_latest()
    @view_cache_response_content()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RestrictedAreaViewSet(
    AutocompleteMixin, LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet
):
    model = RestrictedArea
    serializer_class = RestrictedAreaSerializer
    serializer_autocomplete_class = RestrictedAreaAutoCompleteSerializer
    serializer_autocomplete_bbox_class = RestrictedAreaAutoCompleteBBoxSerializer
    autocomplete_search_fields = ["name"]

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator."""
        language = get_language()
        geojson_lookup = None
        latest_saved = self.model.latest_updated(type_id=self.kwargs.get("type_pk"))
        geojson_lookup = "{}_restricted_area_{}_{}_{}_geojson_layer".format(
            language,
            self.kwargs.get("type_pk", "all"),
            latest_saved.isoformat() if latest_saved else "no_data",
            self.request.user.pk if settings.SURICATE_WORKFLOW_ENABLED else "",
        )
        return geojson_lookup

    def get_queryset(self):
        type_pk = self.kwargs.get("type_pk")
        qs = super().get_queryset()
        if type_pk:
            get_object_or_404(RestrictedAreaType, pk=type_pk)
            qs = qs.filter(area_type=type_pk)
        return qs

    def get_queryset_autocomplete(self):
        return self.model.objects.only("name", "id")

    def get_queryset_autocomplete_bbox(self):
        return self.model.objects.only("name", "envelope")


class DistrictViewSet(
    AutocompleteMixin, LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet
):
    model = District
    serializer_class = DistrictSerializer
    serializer_autocomplete_class = DistrictAutoCompleteSerializer
    serializer_autocomplete_bbox_class = DistrictAutoCompleteBBoxSerializer
    autocomplete_search_fields = ["name"]

    def get_queryset_autocomplete(self):
        return self.model.objects.only("name", "id")

    def get_queryset_autocomplete_bbox(self):
        return self.model.objects.only("name", "envelope")


class CityViewSet(
    AutocompleteMixin, LandGeoJSONAPIViewMixin, viewsets.ReadOnlyModelViewSet
):
    model = City
    autocomplete_search_fields = ["name", "code"]
    serializer_class = CitySerializer
    serializer_autocomplete_class = CityAutoCompleteSerializer
    serializer_autocomplete_bbox_class = CityAutoCompleteBBoxSerializer

    def get_queryset_autocomplete(self):
        return self.model.objects.only("name", "code", "id")

    def get_queryset_autocomplete_bbox(self):
        return self.model.objects.only("name", "code", "envelope")
