from hashlib import md5

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils.translation import activate

from rest_framework.response import Response

from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.cache import ListCacheResponseMixin
from geotrek.api.v2.decorators import cache_response_detail
from geotrek.common import models as common_models
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.trekking.models import Trek


class TargetPortalViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.TargetPortalSerializer
    queryset = common_models.TargetPortal.objects.all()


class ThemeViewSet(ListCacheResponseMixin, api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TreksAndSitesAndTourismRelatedPortalThemeFilter,)
    serializer_class = api_serializers.ThemeSerializer
    queryset = common_models.Theme.objects.all()

    def get_list_cache_key(self):
        """ return specific list cache key based on list last_update object """
        last_update = self.get_queryset().model.last_update_and_count.get('last_update')
        last_update_trek = Trek.last_update_and_count.get('last_update')
        last_update_touristic_content = TouristicContent.last_update_and_count.get('last_update')
        last_update_touristic_event = TouristicEvent.last_update_and_count.get('last_update')

        last_updates = [
            last_update.isoformat() if last_update else '0000-00-00',
            last_update_trek.isoformat() if last_update_trek else '0000-00-00',
            last_update_touristic_content.isoformat() if last_update_touristic_content else '0000-00-00',
            last_update_touristic_event.isoformat() if last_update_touristic_event else '0000-00-00',
        ]
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            from geotrek.outdoor.models import Site
            list_update_site = Site.last_update_and_count.get('last_update')
            last_updates.append(
                list_update_site.isoformat() if list_update_site else '0000-00-00',
            )

        last_update = max(*last_updates)

        return f"{self.get_base_cache_string()}:{last_update}"

    def list_cache_key_func(self, **kwargs):
        """ cache key md5 for list viewset action """
        return md5(self.get_list_cache_key().encode("utf-8")).hexdigest()

    @cache_response_detail()
    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.Theme, pk=pk)
        serializer = api_serializers.ThemeSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class SourceViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TreksAndSitesRelatedPortalFilter,)
    serializer_class = api_serializers.RecordSourceSerializer
    queryset = common_models.RecordSource.objects.all()

    @cache_response_detail()
    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.RecordSource, pk=pk)
        serializer = api_serializers.RecordSourceSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class ReservationSystemViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.RelatedPortalStructureOrReservationSystemFilter,)
    serializer_class = api_serializers.ReservationSystemSerializer
    queryset = common_models.ReservationSystem.objects.all()

    @cache_response_detail()
    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.ReservationSystem, pk=pk)
        serializer = api_serializers.ReservationSystemSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class LabelViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TreksAndSitesRelatedPortalFilter,
                                                                     api_filters.GeotrekLabelFilter)
    serializer_class = api_serializers.LabelSerializer
    queryset = common_models.Label.objects.all()

    @cache_response_detail()
    def retrieve(self, request, pk=None, format=None):
        # Allow to retrieve objects even if not visible in list view
        elem = get_object_or_404(common_models.Label, pk=pk)
        serializer = api_serializers.LabelSerializer(elem, many=False, context={'request': request})
        return Response(serializer.data)


class OrganismViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.OrganismSerializer
    queryset = common_models.Organism.objects.all()


class FileTypeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.FileTypeSerializer
    queryset = common_models.FileType.objects.all()


class HDViewPointViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.HDViewPointSerializer
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.TrekAndSiteAndPOIRelatedPublishedNotDeletedByPortalFilter,)

    def get_queryset(self):
        activate(self.request.GET.get('language'))
        return common_models.HDViewPoint.objects \
            .prefetch_related('content_object') \
            .annotate(geom_transformed=Transform(F('geom'), settings.API_SRID)) \
            .order_by('title')  # Required for reliable pagination
