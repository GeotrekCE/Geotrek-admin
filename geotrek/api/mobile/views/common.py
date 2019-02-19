from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import response
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.mobile.serializers import common as api_serializers
from geotrek.flatpages.models import FlatPage
from geotrek.trekking.models import DifficultyLevel, Practice, Accessibility, Route, Theme, TrekNetwork
from geotrek.tourism.models import InformationDesk
from geotrek.zoning.models import City


class SettingsView(APIView):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get(self, request, *args, **kwargs):
        return response.Response({
            'filters': [
                {
                    "id": "difficulties",
                    "type": "contains"
                },
                {
                    "id": "length",
                    "type": "interval"
                },
                {
                    "id": "cities",
                    "type": "contains"
                },
                {
                    "id": "accessibilities",
                    "type": "contains"
                },
                {
                    "id": "practices",
                    "type": "contains"
                },
                {
                    "id": "duration",
                    "type": "interval"
                },
                {
                    "id": "themes",
                    "type": "contains"
                },
                {
                    "id": "routes",
                    "type": "contains"
                }
            ],
            'data': [
                {
                    'id': 'difficulties',
                    'name': _('difficulties'),
                    'values': api_serializers.DifficultySerializer(DifficultyLevel.objects.all().order_by('pk'),
                                                                   many=True,
                                                                   context={'request': request}).data
                },
                {
                    'id': 'practices',
                    'name': _('practices'),
                    'values': api_serializers.PracticeSerializer(Practice.objects.all().order_by('pk'),
                                                                 many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'accessibilities',
                    'name': _('accessibilities'),
                    'values': api_serializers.PracticeSerializer(Accessibility.objects.all().order_by('pk'), many=True,
                                                                 context={'request': request}).data,
                },
                {
                    'id': 'routes',
                    'name': _('routes'),
                    'values': api_serializers.RouteSerializer(Route.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'themes',
                    'name': _('themes'),
                    'values': api_serializers.ThemeSerializer(Theme.objects.all().order_by('pk'), many=True,
                                                              context={'request': request}).data,
                },
                {
                    'id': 'networks',
                    'name': _('networks'),
                    'values': api_serializers.NetworkSerializer(TrekNetwork.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
                },
                {
                    'id': 'informationdesks',
                    'name': _('informationdesks'),
                    'values': api_serializers.InformationDeskSerializer(InformationDesk.objects.all().order_by('pk'),
                                                                        many=True,
                                                                        context={'request': request}).data,
                },
                {
                    'id': 'cities',
                    'name': _('cities'),
                    'values': api_serializers.CitySerializer(City.objects.all().order_by('pk'), many=True,
                                                             context={'request': request}).data
                }
            ]
        })


class FlatPageViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    Use HTTP basic authentication to access this endpoint.
    """
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    serializer_class = api_serializers.FlatPageListSerializer
    serializer_detail_class = api_serializers.FlatPageDetailSerializer
    queryset = FlatPage.objects.all().order_by('pk')
