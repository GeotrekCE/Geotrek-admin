from django_filters import FilterSet

from .models import Trek, POI


class TrekFilter(FilterSet):
    class Meta:
        model = Trek
        fields = ['difficulty']


class POIFilter(FilterSet):
    class Meta:
        model = POI
        fields = ['type']
