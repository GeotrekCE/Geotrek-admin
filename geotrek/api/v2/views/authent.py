from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from geotrek.api.v2 import serializers as api_serializers
from geotrek.authent import models as authent_models


class StructureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    serializer_class = api_serializers.StructureSerializer
    queryset = authent_models.Structure.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
