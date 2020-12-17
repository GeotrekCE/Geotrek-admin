from django.conf import settings
from django.db.models import F

from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.api.v2.functions import Transform
from geotrek.outdoor import models as outdoor_models


class SiteViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (api_filters.GeotrekSiteFilter,)
    serializer_class = api_serializers.SiteSerializer
    queryset = outdoor_models.Site.objects \
        .annotate(geom_transformed=Transform(F('geom'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination


class OutdoorPracticeViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.OutdoorPracticeSerializer
    queryset = outdoor_models.Practice.objects \
        .order_by('pk')  # Required for reliable pagination


class SiteTypeViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.SiteTypeSerializer
    queryset = outdoor_models.SiteType.objects \
        .order_by('pk')  # Required for reliable pagination
