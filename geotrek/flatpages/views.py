from rest_framework import permissions as rest_permissions
from rest_framework import viewsets

from geotrek.flatpages.serializers import FlatPageSerializer
from geotrek.flatpages import models as flatpages_models


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing flat pages instances.
    """
    model = flatpages_models.FlatPage
    serializer_class = FlatPageSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return flatpages_models.FlatPage.objects.filter(published=True)
