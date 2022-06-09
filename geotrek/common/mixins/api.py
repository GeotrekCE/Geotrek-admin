from django.contrib.gis.db.models.functions import Transform
from mapentity.settings import API_SRID
from rest_framework import viewsets, permissions


class APIViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_serializer_class(self):
        renderer, media_type = self.perform_content_negotiation(self.request)
        if getattr(renderer, 'format') == 'geojson':
            return self.geojson_serializer_class
        else:
            return self.serializer_class

    def get_queryset(self):
        return super().get_queryset().annotate(api_geom=Transform("geom", API_SRID))
