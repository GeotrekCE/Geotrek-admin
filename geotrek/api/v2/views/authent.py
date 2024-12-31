from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.decorators import cache_response_detail
from geotrek.authent import models as authent_models


class StructureViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.RelatedPortalStructureFilter,)
    serializer_class = api_serializers.StructureSerializer
    queryset = authent_models.Structure.objects.all()

    @cache_response_detail()
    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(authent_models.Structure, pk=pk)
        serializer = api_serializers.StructureSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)
