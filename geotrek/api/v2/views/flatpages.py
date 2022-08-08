from django.db.models.query import Prefetch

from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.common.models import Attachment
from geotrek.flatpages import models as flatpages_models


class FlatPageViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (
        api_filters.FlatPageFilter,
        api_filters.UpdateOrCreateDateFilter
    )
    serializer_class = api_serializers.FlatPageSerializer
    queryset = flatpages_models.FlatPage.objects.order_by('order', 'pk') \
        .prefetch_related(Prefetch('attachments',
                                   queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure')))  # Required for reliable pagination
