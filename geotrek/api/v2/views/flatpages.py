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
from geotrek.common.models import Attachment
from geotrek.flatpages import models as flatpages_models
from modeltranslation.utils import build_localized_fieldname


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
            data.append(self._recursive_node_to_dict(n))

        return Response(data)

    def _check_page_published(self, node):
        # FIXME: duplicates a lot of GeotrekPublishedFilter.filter_queryset
        if not node.page:
            return True

        page = node.page

        language = self.request.GET.get('language', 'all')
        associated_published_fields = [f.name for f in page._meta.get_fields() if f.name.startswith('published')]

        if len(associated_published_fields) == 1:
            # the FlatPage model published field is not translated
            return page.published
        elif len(associated_published_fields) > 1:
            # the FlatPage model published field is translated
            if language == 'all':
                # no language specified. Include if at least one language published.
                for lang in settings.MODELTRANSLATION_LANGUAGES:
                    field_name = build_localized_fieldname('published', lang)
                    if getattr(page, field_name):
                        return True
                return False
            else:
                # a language is specified, return the publication status for that language.
                field_name = build_localized_fieldname('published', language)
                return getattr(page, field_name)

    def _recursive_node_to_dict(self, node):
        result = self.get_serializer(instance=node).data
        children = [self._recursive_node_to_dict(c) for c in self.filter_queryset(node.get_children()) if self._check_page_published(c)]
        if children:
            result["children"] = children
        return result


# class FlatPageRetrieveView(RetrieveAPIView):
#     serializer_class = api_serializers.FlatPageSerializer
#     queryset = flatpages_models.FlatPage.objects.all()
#
#     permission_classes = [IsAuthenticatedOrReadOnly, ] if settings.API_IS_PUBLIC else [IsAuthenticated, ]
#     authentication_classes = [BasicAuthentication, SessionAuthentication]
#     renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer, ] if settings.DEBUG else [
#         renderers.JSONRenderer, ]
#
#
# class FlatPageTreeView(GenericAPIView):
#     # from https://stackoverflow.com/questions/21112302/how-to-serialize-hierarchical-relationship-in-django-rest
#     serializer_class = api_serializers.FlatPageSerializer
#     queryset = flatpages_models.FlatPage.objects.filter(depth=1)
#     filter_backends = (GeotrekPublishedFilter, )
#
#     permission_classes = [IsAuthenticatedOrReadOnly, ] if settings.API_IS_PUBLIC else [IsAuthenticated, ]
#     authentication_classes = [BasicAuthentication, SessionAuthentication]
#     renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer, ] if settings.DEBUG else [
#         renderers.JSONRenderer, ]
#
#     def get(self, request, *args, **kwargs):
#         root_items = self.filter_queryset(self.queryset).all()
#
#         data = []
#         for n in root_items:
#             data.append(self._recursive_node_to_dict(n))
#
#         return Response(data)
#
#     def _recursive_node_to_dict(self, node):
#         result = self.get_serializer(instance=node).data
#         children = [self._recursive_node_to_dict(c) for c in node.get_children()]
#         if children:
#             result["children"] = children
#         return result
