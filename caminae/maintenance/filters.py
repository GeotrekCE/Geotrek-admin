from django_filters import FilterSet

from .models import Intervention, Project


class InterventionFilter(FilterSet):
    class Meta:
        model = Intervention
        fields = ['status']


class ProjectFilter(FilterSet):
    class Meta:
        model = Project
        fields = ['begin_year', 'end_year']
