from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import renderers

from django.conf import settings
from django.db.models.query import Prefetch
from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.api.v2.filters import GeotrekPublishedFilter
from geotrek.api.v2 import utils as api_utils
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


class MenuItemRetrieveView(RetrieveAPIView):
    serializer_class = api_serializers.MenuItemDetailsSerializer
    queryset = flatpages_models.MenuItem.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ] if settings.API_IS_PUBLIC else [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer, ] if settings.DEBUG else [
        renderers.JSONRenderer, ]
    filter_backends = (
        GeotrekPublishedFilter,
    )


class MenuItemTreeView(GenericAPIView):
    # from https://stackoverflow.com/questions/21112302/how-to-serialize-hierarchical-relationship-in-django-rest
    serializer_class = api_serializers.MenuItemSerializer
    queryset = flatpages_models.MenuItem.objects.filter(depth=1)
    filter_backends = (
        GeotrekPublishedFilter,
        api_filters.MenuItemFilter,
    )
    permission_classes = [IsAuthenticatedOrReadOnly, ] if settings.API_IS_PUBLIC else [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer, ] if settings.DEBUG else [
        renderers.JSONRenderer, ]

    def get(self, request, *args, **kwargs):
        root_items = self.filter_queryset(self.get_queryset()).all()

        data = []
        for n in root_items:
            if self._check_page_published(n):
                data.append(self._recursive_node_to_dict(n))

        return Response(data)

    def _check_page_published(self, node):
        if not node.page:
            return True
        page = node.page
        language = self.request.GET.get('language', 'all')
        return api_utils.is_published(page, language)

    def _recursive_node_to_dict(self, node):
        result = self.get_serializer(instance=node).data
        children = [self._recursive_node_to_dict(c) for c in self.filter_queryset(node.get_children()) if self._check_page_published(c)]
        result["children"] = children
        return result
