from django.db.models.query import Prefetch

from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.api.v2.filters import GeotrekPublishedFilter
from geotrek.common.models import Attachment
from geotrek.flatpages import models as flatpages_models


class FlatPageViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (
        api_filters.FlatPageFilter,
        api_filters.UpdateOrCreateDateFilter
    )
    serializer_class = api_serializers.FlatPageSerializer
    queryset = flatpages_models.FlatPage.objects.order_by('pk') \
        .prefetch_related(Prefetch('attachments',
                                   queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure')))  # Required for reliable pagination



from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class MenuItemViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends
    serializer_class = api_serializers.MenuItemSerializer
    queryset = flatpages_models.MenuItem.objects.filter(depth=1).order_by('path')


class MenuItemTreeView(GenericAPIView):
    """from https://stackoverflow.com/questions/21112302/how-to-serialize-hierarchical-relationship-in-django-rest"""
    serializer_class = api_serializers.MenuItemSerializer
    queryset = flatpages_models.MenuItem.objects.filter(depth=1)
    filter_backends = GeotrekPublishedFilter

    def get(self, request, *args, **kwargs):
        root_items = self.queryset.all()

        data = []
        for n in root_items:
            data.append(self._recursive_node_to_dict(n))

        return Response(data)

    def _recursive_node_to_dict(self, node):
        result = self.get_serializer(instance=node).data
        children = [self._recursive_node_to_dict(c) for c in node.get_children()]
        if children:
            result["children"] = children
        return result


class FlatPageTreeView(GenericAPIView):
    """from https://stackoverflow.com/questions/21112302/how-to-serialize-hierarchical-relationship-in-django-rest"""
    serializer_class = api_serializers.FlatPageSerializer
    queryset = flatpages_models.FlatPage.objects.filter(depth=1)
    filter_backends = (GeotrekPublishedFilter, )

    def get(self, request, *args, **kwargs):
        root_items = self.filter_queryset(self.queryset).all()

        data = []
        for n in root_items:
            data.append(self._recursive_node_to_dict(n))

        return Response(data)

    def _recursive_node_to_dict(self, node):
        result = self.get_serializer(instance=node).data
        children = [self._recursive_node_to_dict(c) for c in node.get_children()]
        if children:
            result["children"] = children
        return result
