from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.utils import filter_queryset_related_objects_published
from geotrek.authent import models as authent_models


class StructureViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRelatedPortalStructureFilter,)
    serializer_class = api_serializers.StructureSerializer

    def get_queryset(self):
        qs = authent_models.Structure.objects.all()
        set_1 = filter_queryset_related_objects_published(qs, self.request, 'trek')
        set_2 = filter_queryset_related_objects_published(qs, self.request, 'touristiccontent')
        return (set_1 | set_2).distinct()
