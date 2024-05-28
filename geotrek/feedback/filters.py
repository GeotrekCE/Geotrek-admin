from django.utils.translation import gettext_lazy as _
from django_filters import MultipleChoiceFilter
from mapentity.filters import MapEntityFilterSet

from geotrek.zoning.filters import ZoningFilterSet

from .models import Report


class ReportFilterSet(ZoningFilterSet, MapEntityFilterSet):
    year_insert = MultipleChoiceFilter(
        label=_("Creation year"),
        field_name='date_insert__year',
        choices=lambda: Report.objects.year_insert_choices()
    )
    year_update = MultipleChoiceFilter(
        label=_("Update year"),
        field_name='date_update__year',
        choices=lambda: Report.objects.year_update_choices()
    )

    class Meta(MapEntityFilterSet.Meta):
        model = Report
        fields = ['activity', 'category', 'status', 'problem_magnitude', 'assigned_user']


class ReportEmailFilterSet(ReportFilterSet):

    class Meta(MapEntityFilterSet.Meta):
        model = Report
        fields = ['activity', 'email', 'category', 'status', 'problem_magnitude', 'assigned_user']
