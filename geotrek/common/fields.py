from django_filters.fields import RangeField

from .widgets import OneLineRangeWidget


class OneLineRangeField(RangeField):
    widget = OneLineRangeWidget(attrs={'class': 'minmax-field'})
