from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets
from geotrek.authent import models as authent_models


class StructureViewSet(api_viewsets.GeotrekViewset):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    serializer_class = api_serializers.StructureSerializer
    queryset = authent_models.Structure.objects.all()
