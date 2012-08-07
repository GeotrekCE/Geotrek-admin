from django_filters import FilterSet

from .models import Intervention


class InterventionFilter(FilterSet):
    class Meta:
        model = Intervention
        fields = ['status']
