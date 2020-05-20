import logging

from django.contrib.gis.db.models.functions import Transform
from django.views.generic.list import ListView

from djgeojson.views import GeoJSONLayerView
from rest_framework import viewsets

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
    geometry_field = 'simplified_geom'

    def __init__(self, *args, **kwargs):
        super(MapEntityLayer, self).__init__(*args, **kwargs)
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
    @view_cache_latest()
    def dispatch(self, *args, **kwargs):
        return super(MapEntityLayer, self).dispatch(*args, **kwargs)

    @view_cache_response_content()
    def render_to_response(self, context, **response_kwargs):
        return super(MapEntityLayer, self).render_to_response(context, **response_kwargs)


class MapEntityJsonList(JSONResponseMixin, BaseListView, ListView):
    """
    Return objects list as a JSON that will populate the Jquery.dataTables.
    """

    @classmethod
    def get_entity_kind(cls):
        return mapentity_models.ENTITY_JSON_LIST

    def get_context_data(self, **kwargs):
        """
        Override the most important part of JSONListView... (paginator)
        """
        serializer = mapentity_serializers.DatatablesSerializer()
        return serializer.serialize(self.get_queryset(),
                                    fields=self.columns,
                                    model=self.get_model())

    @view_permission_required()
    @view_cache_latest()
    def dispatch(self, *args, **kwargs):
        return super(BaseListView, self).dispatch(*args, **kwargs)


class MapEntityViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        renderer, media_type = self.perform_content_negotiation(self.request)
        if getattr(renderer, 'format') == 'geojson':
            return self.geojson_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return super().get_queryset().annotate(api_geom=Transform("geom", API_SRID))
