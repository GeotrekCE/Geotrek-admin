import logging
from math import pi
import mercantile

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import Polygon
from django.db.models import Func, Q
from django.core.exceptions import FieldDoesNotExist
from django.views.generic.list import ListView

from djgeojson.views import GeoJSONLayerView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from mapentity import models as mapentity_models
from ..settings import API_SRID, app_settings
from ..decorators import (view_cache_response_content, view_cache_latest,
                          view_permission_required)
from .. import serializers as mapentity_serializers

from .base import BaseListView
from .mixins import FilterListMixin, ModelViewMixin, JSONResponseMixin


logger = logging.getLogger(__name__)


class MapEntityLayer(FilterListMixin, ModelViewMixin, GeoJSONLayerView):
    """
    Take a class attribute `model` with a `latest_updated` method used for caching.
    """

    force2d = True
    srid = API_SRID
    precision = app_settings.get('GEOJSON_PRECISION')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Backward compatibility with django-geojson 1.X
        # for JS ObjectsLayer and rando-trekking application
        # TODO: remove when migrated
        properties = dict([(k, k) for k in self.properties])
        if 'id' not in self.properties:
            properties['id'] = 'pk'
        self.properties = properties

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_LAYER

    @view_permission_required()
    # @view_cache_latest()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @view_cache_response_content()
    def render_to_response(self, context, **response_kwargs):
        return super().render_to_response(context, **response_kwargs)


class MapEntityTileLayer(ModelViewMixin, ListAPIView):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    model = None

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_TILE_LAYER

    def get_queryset(self):
        qs = self.queryset
        qs = qs.filter(geom__intersects=self.bbox)
        # qs = qs.filter(length__gte=2 * self.pixel_size)
        return qs.annotate(api_geom=Transform(Func('geom', self.pixel_size, function='ST_SimplifyPreserveTopology'), API_SRID))

    @property
    def pixel_size(self):
        tile_pixel_size = 512
        equatorial_radius_wgs84 = 6378137
        circumference = 2 * pi * equatorial_radius_wgs84
        return circumference / tile_pixel_size / 2 ** int(self.kwargs['z'])

    @property
    def bbox(self):
        # define bounds from x y z and create polygon from bounds
        bounds = mercantile.bounds(int(self.kwargs['x']), int(self.kwargs['y']), int(self.kwargs['z']))
        west, south = mercantile.xy(bounds.west, bounds.south)
        east, north = mercantile.xy(bounds.east, bounds.north)
        bbox = Polygon.from_bbox((west, south, east, north))
        bbox.srid = 3857  # WGS84 SRID
        # transform the polygon to match with db srid
        bbox.transform(settings.SRID)
        return bbox


class MapEntityJsonList(JSONResponseMixin, BaseListView, ListView):
    """
    Return objects list as a JSON that will populate the Jquery.dataTables.
    """
    def searching(self, qs):
        search = self.request.GET.get('sSearch', None)
        searching_method = 'icontains'
        q = Q()
        if search:
            for col in self.columns:
                try:
                    field = self.get_model()._meta.get_field(col)
                    if field.get_internal_type() == "CharField":
                        q |= Q(**{'{0}__{1}'.format(col, searching_method): search})
                except (FieldDoesNotExist, AttributeError):
                    # AttributeError is for generic relation (target)
                    pass
            qs = qs.filter(q)
        return qs

    def ordering_qs(self, qs):
        number_columns_sort = int(self.request.GET.get('iSortingCols', 0))
        for i in range(number_columns_sort):
            sort_column = int(self.request.GET.get('iSortCol_{0}'.format(i), 0))
            sort_direction = self.request.GET.get('sSortDir_{0}'.format(i), 'asc')
            try:
                sdir = '-' if sort_direction == 'desc' else ''
                sortcol = self.columns[sort_column]
                self.get_model()._meta.get_field(sortcol)
                if sortcol:
                    qs = qs.order_by('{0}{1}'.format(sdir, sortcol.replace('.', '__')))
            except FieldDoesNotExist:
                if sort_direction == 'asc':

                    qs = sorted(qs, key=lambda t: -1 * float('inf') if getattr(t, sortcol) is None else getattr(t, sortcol))
                else:
                    qs = sorted(qs, key=lambda t: -1 * float('inf') if getattr(t, sortcol) is None else getattr(t, sortcol), reverse=True)
        return qs

    def paging(self, qs):
        limit = int(self.request.GET.get('iDisplayLength', 10))
        start = int(self.request.GET.get('iDisplayStart', 0))
        end = start + limit
        return qs[start:end]

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_JSON_LIST

    def get_context_data(self, queryset=None, **kwargs):
        """
        Override the most important part of JSONListView... (paginator)
        """
        qs = self.get_queryset() if queryset is None else queryset
        # store the total number of records
        total_records = qs.count()
        # filtering the queryset according to the search field
        qs = self.searching(qs)
        # number of records after filtering.
        total_display_records = qs.count()
        # order the queryset
        qs = self.ordering_qs(qs)
        # paging the queryset
        qs = self.paging(qs)

        serializer = mapentity_serializers.DatatablesSerializer()
        return serializer.serialize(
            qs,
            fields=self.columns,
            model=self.get_model(),
            total_records=total_records,
            total_display_records=total_display_records,
            echo=int(self.request.GET.get('sEcho', 0))
        )

    @view_permission_required()
    @view_cache_latest()
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class MapEntityViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        renderer, media_type = self.perform_content_negotiation(self.request)
        if getattr(renderer, 'format') == 'geojson':
            return self.geojson_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return super().get_queryset().annotate(api_geom=Transform("geom", API_SRID))
