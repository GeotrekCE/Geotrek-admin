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


class InformationDeskViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InformationDeskSerializer
    queryset = tourism_models.InformationDesk.objects.all()
