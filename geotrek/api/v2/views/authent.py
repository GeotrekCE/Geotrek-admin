from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.authent import models as authent_models


class StructureViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalStructureFilter,)
    serializer_class = api_serializers.StructureSerializer
    queryset = authent_models.Structure.objects.all()
