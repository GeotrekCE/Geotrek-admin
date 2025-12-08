from django.http import HttpResponse
from django.views.generic import ListView

from geotrek.cirkwi.filters import CirkwiPOIFilterSet, CirkwiTrekFilterSet
from geotrek.cirkwi.serializers import CirkwiPOISerializer, CirkwiTrekSerializer
from geotrek.trekking.models import POI, Trek


class CirkwiTrekView(ListView):
    model = Trek

    def get_queryset(self):
        qs = Trek.objects.existing()
        qs = qs.filter(published=True)
        qs = CirkwiTrekFilterSet(self.request.GET, queryset=qs).qs
        return qs

    def get(self, request):
        response = HttpResponse(content_type="application/xml")
        serializer = CirkwiTrekSerializer(request, response, request.GET)
        treks = self.get_queryset()
        serializer.serialize(treks)
        return response


class CirkwiPOIView(ListView):
    model = POI

    def get_queryset(self):
        qs = POI.objects.existing()
        qs = qs.filter(published=True)
        qs = CirkwiPOIFilterSet(self.request.GET, queryset=qs).qs
        return qs

    def get(self, request):
        response = HttpResponse(content_type="application/xml")
        serializer = CirkwiPOISerializer(request, response, request.GET)
        pois = self.get_queryset()
        serializer.serialize(pois)
        return response
