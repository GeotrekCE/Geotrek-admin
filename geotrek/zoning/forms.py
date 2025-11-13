from dal import autocomplete
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from geotrek.zoning.models import City, District


class MapFilterForm(forms.Form):
    if settings.LAND_BBOX_CITIES_ENABLED and City.objects.exists():
        bbox_city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            widget=autocomplete.ModelSelect2(
                url="zoning:city-autocomplete-bbox",
                attrs={
                    "data-placeholder": _("City"),
                    #'data-theme': 'bootstrap4'
                },
            ),
            required=False,
        )

    if settings.LAND_BBOX_DISTRICTS_ENABLED and District.objects.exists():
        bbox_district = forms.ModelChoiceField(
            queryset=District.objects.all(),
            widget=autocomplete.ModelSelect2(
                url="zoning:district-autocomplete-bbox",
                attrs={
                    "data-placeholder": _("District"),
                    #'data-theme': 'bootstrap4'
                },
            ),
            required=False,
        )
