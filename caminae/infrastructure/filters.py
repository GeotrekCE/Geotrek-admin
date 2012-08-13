from django_filters import FilterSet

from .models import Infrastructure, Signage


class InfrastructureFilter(FilterSet):
    class Meta:
        model = Infrastructure
        fields = ['type']


class SignageFilter(FilterSet):
    class Meta:
        model = Signage
        fields = ['type']
