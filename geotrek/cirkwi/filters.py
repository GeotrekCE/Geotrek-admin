from django_filters import ModelMultipleChoiceFilter, FilterSet
from django_filters.fields import ModelChoiceField
from geotrek.authent.models import Structure
from geotrek.common.models import TargetPortal
from geotrek.trekking.models import POI, Trek
from django.forms import ValidationError


class ComaSeparatedModelChoiceField(ModelChoiceField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            key = self.to_field_name or 'pk'
            if isinstance(value, self.queryset.model):
                value = getattr(value, key)
            value = self.queryset.filter(**{f'{key}__in': value.split(',')})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value


class ComaSeparatedMultipleModelChoiceFilter(ModelMultipleChoiceFilter):
    field_class = ComaSeparatedModelChoiceField


class CirkwiPOIFilterSet(FilterSet):
    structures = ComaSeparatedMultipleModelChoiceFilter(field_name='structure', required=False,
                                                        queryset=Structure.objects.all())

    class Meta:
        model = POI
        fields = ('structures', )


class CirkwiTrekFilterSet(FilterSet):
    structures = ComaSeparatedMultipleModelChoiceFilter(field_name='structure', required=False,
                                                        queryset=Structure.objects.all())
    portals = ComaSeparatedMultipleModelChoiceFilter(field_name='portal', required=False,
                                                     queryset=TargetPortal.objects.all())

    class Meta:
        model = Trek
        fields = ('structures', 'portals', )
