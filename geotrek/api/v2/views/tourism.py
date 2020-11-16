from django.conf import settings
from django.db.models import F

from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.api.v2.functions import Transform
from geotrek.tourism import models as tourism_models


class TouristicContentViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (api_filters.GeotrekTouristicContentFilter,)
    serializer_class = api_serializers.TouristicContentSerializer
    queryset = tourism_models.TouristicContent.objects.existing()\
        .select_related('category', 'reservation_system') \
        .prefetch_related('source', 'themes', 'type1', 'type2') \
        .annotate(geom_transformed=Transform(F('geom'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination

    def get_serializer_class(self):
        base_serializer_class = super(TouristicContentViewSet, self).get_serializer_class()
        format_output = self.request.query_params.get('format', 'json')
        return api_serializers.override_serializer(format_output, base_serializer_class)


class InformationDeskViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InformationDeskSerializer
    queryset = tourism_models.InformationDesk.objects.all()
