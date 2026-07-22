from crispy_forms.layout import Div
from dal import autocomplete
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.zoning.models import City, District, RestrictedArea, VigilanceArea


class MapFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.LAND_BBOX_CITIES_ENABLED and City.objects.exists():
            self.fields["bbox_city"] = forms.ModelChoiceField(
                queryset=City.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url="zoning:city-autocomplete-bbox",
                    attrs={
                        "data-placeholder": _("City"),
                    },
                ),
                required=False,
            )

        if settings.LAND_BBOX_DISTRICTS_ENABLED and District.objects.exists():
            self.fields["bbox_district"] = forms.ModelChoiceField(
                queryset=District.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url="zoning:district-autocomplete-bbox",
                    attrs={
                        "data-placeholder": _("District"),
                    },
                ),
                required=False,
            )

        if settings.LAND_BBOX_AREAS_ENABLED and RestrictedArea.objects.exists():
            self.fields["bbox_restrictedarea"] = forms.ModelChoiceField(
                queryset=RestrictedArea.objects.all(),
                widget=autocomplete.ModelSelect2(
                    url="zoning:restrictedarea-autocomplete-bbox",
                    attrs={
                        "data-placeholder": _("Restricted area"),
                    },
                ),
                required=False,
            )


class VigilanceAreaForm(CommonForm):
    geomfields = ["geom"]
    fieldslayout = [
        Div(
            "structure",
            "name",
            "vigilance_area_type",
            "practicability",
            "published",
            "description",
            "practical_info",
            "external_info_url",
            "sources",
            "portals",
            "provider",
            "eid",
        )
    ]

    class Meta(CommonForm.Meta):
        model = VigilanceArea
        fields = [
            *CommonForm.Meta.fields,
            "name",
            "structure",
            "description",
            "provider",
            "eid",
            "vigilance_area_type",
            "external_info_url",
            "practicability",
            "practical_info",
            "sources",
            "portals",
            "published",
            "geom",
        ]
