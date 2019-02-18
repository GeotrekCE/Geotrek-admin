from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import response

from geotrek.api.mobile.serializers import common as api_serializers
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
            'difficulty': api_serializers.DifficultySerializer(DifficultyLevel.objects.all().order_by('pk'), many=True,
                                                               context={'request': request}).data,
            'practice': api_serializers.PracticeSerializer(Practice.objects.all().order_by('pk'), many=True,
                                                           context={'request': request}).data,
            'accessibility': api_serializers.PracticeSerializer(Accessibility.objects.all().order_by('pk'), many=True,
                                                                context={'request': request}).data,
            'route': api_serializers.RouteSerializer(Route.objects.all().order_by('pk'), many=True,
                                                     context={'request': request}).data,
            'theme': api_serializers.ThemeSerializer(Theme.objects.all().order_by('pk'), many=True,
                                                     context={'request': request}).data,
            'network': api_serializers.NetworkSerializer(TrekNetwork.objects.all().order_by('pk'), many=True,
                                                         context={'request': request}).data,
            'informationdesk': api_serializers.InformationDeskSerializer(InformationDesk.objects.all().order_by('pk'),
                                                                         many=True,
                                                                         context={'request': request}).data,
            'city': api_serializers.CitySerializer(City.objects.all().order_by('pk'), many=True,
                                                   context={'request': request}).data
        })
