from django.conf import settings
from mapentity.views import MapEntityViewSet
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from geotrek.common.renderers import GTAMRenderer


class GeotrekMapentityViewSet(MapEntityViewSet):
    """Custom MapentityViewSet for geotrek."""
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    mapentity_list_class = []
    gtam_serializer_class = None
    renderer_classes = MapEntityViewSet.renderer_classes + [GTAMRenderer]

    def get_columns(self):
        return self.mapentity_list_class.columns

    def get_serializer_class(self):
        """Use specific Serializer for GeoJSON"""
        renderer, media_type = self.perform_content_negotiation(self.request)
        if getattr(renderer, "format") == "gtam" and self.gtam_serializer_class:
            return self.gtam_serializer_class
        return super().get_serializer_class()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        columns = self.get_columns()

        if columns:
            context["request"].query_params._mutable = True
            # in combination with DynamicFieldsMixin on serializer
            # this permit to optimize data serialization with only required columns
            context["request"].query_params["fields"] = ",".join(columns)
        return context
