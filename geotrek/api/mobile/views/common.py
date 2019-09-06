from __future__ import unicode_literals

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import response
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.mobile.serializers import common as api_serializers
from geotrek.flatpages.models import FlatPage
from geotrek.trekking.models import DifficultyLevel, Practice, Accessibility, Route, Theme, TrekNetwork, POIType
from geotrek.tourism.models import (InformationDeskType, TouristicContentType, TouristicEventType,
                                    TouristicContentCategory)
from geotrek.zoning.models import City, District


class SettingsView(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, *args, **kwargs):
        filters = []
        for filter in settings.ENABLED_MOBILE_FILTERS:
            if filter == 'difficulty' and DifficultyLevel.objects.exists():
                filters.append({
                    "id": "difficulty",
                    "type": "contains",
                    "showAllLabel": _("Show all difficulties"),
                    "hideAllLabel": _("Hide all difficulties")
                })
            if filter == 'lengths':
                filters.append({
                    "id": "lengths",
                    "type": "interval",
                    "showAllLabel": _("Show all lengths"),
                    "hideAllLabel": _("Hide all lengths")
                })
            if filter == 'ascent':
                filters.append({
                    "id": "ascent",
                    "type": "interval",
                    "showAllLabel": _("Show all ascents"),
                    "hideAllLabel": _("Hide all ascents")
                })
            if filter == 'districts' and District.objects.exists():
                filters.append({
                    "id": "districts",
                    "type": "contains",
                    "showAllLabel": _("Show all districts"),
                    "hideAllLabel": _("Hide all districts")
                })
            if filter == 'cities' and City.objects.exists():
                filters.append({
                    "id": "cities",
                    "type": "contains",
                    "showAllLabel": _("Show all cities"),
                    "hideAllLabel": _("Hide all cities")
                })
            if filter == 'accessibilities' and Accessibility.objects.exists():
                filters.append({
                    "id": "accessibilities",
                    "type": "contains",
                    "showAllLabel": _("Show all accessibilities"),
                    "hideAllLabel": _("Hide all accessibilities")
                })
            if filter == 'practice' and Practice.objects.exists():
                filters.append({
                    "id": "practice",
                    "type": "contains",
                    "showAllLabel": _("Show all practices"),
                    "hideAllLabel": _("Hide all practices")
                })
            if filter == 'durations':
                filters.append({
                    "id": "durations",
                    "type": "interval",
                    "showAllLabel": _("Show all durations"),
                    "hideAllLabel": _("Hide all durations")
                })
            if filter == 'themes' and Theme.objects.exists():
                filters.append({
                    "id": "themes",
                    "type": "contains",
                    "showAllLabel": _("Show all themes"),
                    "hideAllLabel": _("Hide all themes")
                })
            if filter == 'route' and Route.objects.exists():
                filters.append({
                    "id": "route",
                    "type": "contains",
                    "showAllLabel": _("Show all routes"),
                    "hideAllLabel": _("Hide all routes")
                })
        return response.Response({
            'filters': filters,
            'data': [
                {
                    'id': 'length',
                    'name': _('Length'),
                    'values': settings.MOBILE_LENGTH_INTERVALS,
                },
                {
                    'id': 'ascent',
                    'name': _('Ascent'),
                    'values': settings.MOBILE_ASCENT_INTERVALS,
                },
                {
                    'id': 'duration',
                    'name': _('Duration'),
                    'values': settings.MOBILE_DURATION_INTERVALS,

                },
                {
                    'id': 'difficulty',
                    'name': _('Difficulty'),
                    'values': api_serializers.DifficultySerializer(DifficultyLevel.objects.all().order_by('pk'),
                                                                   many=True,
                                                                   context={'request': request}).data
                },
                {
                    'id': 'practice',
                    'name': _('Practice'),
                    'values': api_serializers.PracticeSerializer(Practice.objects.all().order_by('pk'),
                                                                 many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'accessibilities',
                    'name': _('Accessibilities'),
                    'values': api_serializers.AccessibilitySerializer(Accessibility.objects.all().order_by('pk'),
                                                                      many=True, context={'request': request}).data,
                },
                {
                    'id': 'route',
                    'name': _('Route'),
                    'values': api_serializers.RouteSerializer(Route.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'themes',
                    'name': _('Themes'),
                    'values': api_serializers.ThemeSerializer(Theme.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'networks',
                    'name': _('Networks'),
                    'values': api_serializers.NetworkSerializer(TrekNetwork.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'information_desk_types',
                    'name': _('Information Desks Types'),
                    'values': api_serializers.InformationDeskTypeSerializer(InformationDeskType.objects.all()
                                                                            .order_by('pk'),
                                                                            many=True,
                                                                            context={'request': request}).data,
                },
                {
                    'id': 'districts',
                    'name': _('Districts'),
                    'values': api_serializers.DistrictSerializer(District.objects.all().order_by('pk'), many=True,
                                                                 context={'request': request}).data
                },
                {
                    'id': 'cities',
                    'name': _('Cities'),
                    'values': api_serializers.CitySerializer(City.objects.all().order_by('pk'), many=True,
                                                             context={'request': request}).data
                },
                {
                    'id': 'poi_types',
                    'name': _('POI types'),
                    'values': api_serializers.POITypeSerializer(POIType.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'touristiccontent_types',
                    'name': _('Touristic content types'),
                    'values': api_serializers.TouristicContentTypeSerializer(
                        TouristicContentType.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
                {
                    'id': 'touristicevent_types',
                    'name': _('Touristic event types'),
                    'values': api_serializers.TouristicEventTypeSerializer(
                        TouristicEventType.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
                {
                    'id': 'touristiccontent_categories',
                    'name': _('Touristic event types'),
                    'values': api_serializers.TouristicContentCategorySerializer(
                        TouristicContentCategory.objects.all().order_by('pk'),
                        many=True, context={'request': request}).data,
                },
            ]
        })


class FlatPageViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = api_serializers.FlatPageListSerializer
    serializer_detail_class = api_serializers.FlatPageDetailSerializer

    def get_queryset(self, *args, **kwargs):
        qs = FlatPage.objects.filter(target__in=['mobile', 'all'], published=True).order_by('order')
        if self.request.GET.get('portal', '') != '':
            qs = qs.filter(Q(portal__name__in=self.request.GET['portal'].split(',')) | Q(portal=None))
        return qs
