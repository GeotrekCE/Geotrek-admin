from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Fieldset, Layout, Row
from dal import autocomplete
from dal_select2.widgets import Select2Multiple
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from geotrek.common.forms import CommonForm
from geotrek.zoning.choices import MonthChoices, WeekdayChoices
from geotrek.zoning.models import (
    City,
    District,
    RestrictedArea,
    VigilanceArea,
)


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


class VigilancePeriodForm(forms.ModelForm):
    active_days = forms.TypedMultipleChoiceField(
        choices=WeekdayChoices.choices,
        coerce=int,
        required=False,
        widget=Select2Multiple(choices=WeekdayChoices.choices),
        label=_("Active days"),
        help_text=_(
            "Days of the week when the vigilance area is active. Empty equals all week."
        ),
    )
    active_months = forms.TypedMultipleChoiceField(
        choices=MonthChoices.choices,
        coerce=int,
        required=False,
        widget=Select2Multiple(choices=MonthChoices.choices),
        label=_("Active months"),
        help_text=_(
            "Months of the year when the vigilance area is active. Empty equals all year."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields_for_layout = [
            "id",
            Row(
                Column("start_date"),
                Column("end_date"),
                css_class="border-0 p-0",
            ),
            "active_days",
            "active_months",
            "annual",
        ]

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(*fields_for_layout)

    class Meta:
        fields = (
            "id",
            "start_date",
            "end_date",
            "active_days",
            "active_months",
            "annual",
        )
        widgets = {
            "start_date": forms.TextInput(attrs={"type": "date"}),
            "end_date": forms.TextInput(attrs={"type": "date"}),
        }


class VigilanceAreaForm(CommonForm):
    geomfields = ["geom"]
    fieldslayout = [
        Div(
            "structure",
            "name",
            Fieldset(_("Periods")),
            "vigilance_area_type",
            "vigilance_level",
            "impracticable",
            "published",
            "description",
            "practical_info",
            "external_info_url",
            "sources",
            "portals",
            "private_comment",
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
            "eid",
            "vigilance_area_type",
            "external_info_url",
            "impracticable",
            "vigilance_level",
            "practical_info",
            "sources",
            "portals",
            "published",
            "private_comment",
            "geom",
        ]
