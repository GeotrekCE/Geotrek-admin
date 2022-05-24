from mapentity.views import MapEntityViewSet
from rest_framework import permissions


class GeotrekMapentityViewSet(MapEntityViewSet):
    """ Custom MapentityViewSet for geotrek. """

    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_columns(self):
        return []

    def get_serializer_context(self):
        context = super().get_serializer_context()
        columns = self.get_columns()

        if columns:
            context['request'].query_params._mutable = True
            # in combination with DynamicFieldsMixin on serializer
            # this permit to optimize data serialization with only required columns
            context['request'].query_params['fields'] = ','.join(columns)
        return context
