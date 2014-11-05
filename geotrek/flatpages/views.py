from rest_framework import viewsets

from geotrek.flatpages.serializers import FlatPageSerializer
from geotrek.flatpages import models as flatpages_models


class FlatPageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing flat pages instances.
    """
    serializer_class = FlatPageSerializer
    queryset = flatpages_models.FlatPage.objects.all()
