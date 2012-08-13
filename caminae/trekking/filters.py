from django_filters import FilterSet

from .models import Trek


class TrekFilter(FilterSet):
    class Meta:
        model = Trek
        fields = ['difficulty']


class POIFilter(FilterSet):
    class Meta:
        model = Trek
        fields = ['type']
