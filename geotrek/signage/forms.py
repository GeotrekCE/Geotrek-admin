from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout
from django import forms
from django.conf import settings
from django.contrib.gis.forms.fields import GeometryField
from django.db.models import Max
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import MapWidget

from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField
from geotrek.core.widgets import PointTopologyWidget
from geotrek.infrastructure.forms import BaseInfrastructureForm
from geotrek.signage.models import Blade, Line, Signage


class LineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fields_for_layout = [
            "id",
            "number",
            "direction",
            "text",
            "distance",
            "time",
            "pictograms",
        ]

        if not settings.DIRECTION_ON_LINES_ENABLED:
            del self.fields["direction"]
            fields_for_layout.remove("direction")

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(*fields_for_layout)

    class Meta:
        fields = (
            "id",
            "blade",
            "number",
            "direction",
            "text",
            "distance",
            "time",
            "pictograms",
        )


LineFormset = inlineformset_factory(Blade, Line, form=LineForm, extra=1)


class BaseBladeForm(CommonForm):

    fieldslayout = (
        [
            Div(
                "number",
                "direction",
                "type",
                "conditions",
                "color",
                Fieldset(_("Lines")),
            )
        ]
        if settings.LINE_ENABLED
        else [
            Div(
                "number",
                "direction",
                "type",
                "conditions",
                "color",
            )
        ]
    )

    not_hideable_fields = ["direction"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.form_tag = False
        if not self.instance.pk:
            self.signage = kwargs.get("initial", {}).get("signage")
            self.helper.form_action += f"?signage={self.signage.pk}"
        else:
            self.signage = self.instance.signage
        self._set_number_field_initial_value()

        if settings.DIRECTION_ON_LINES_ENABLED:
            del self.fields["direction"]

    def save(self, *args, **kwargs):
        self.instance.signage = self.signage
        return super(CommonForm, self).save(*args, **kwargs)

    def clean_number(self):
        blades = self.signage.blade_set.all()
        if self.instance.pk:
            blades = blades.exclude(number=self.instance.number)
        already_used = ", ".join(
            [str(number) for number in blades.values_list("number", flat=True)]
        )
        if blades.filter(number=self.cleaned_data["number"]).exists():
            raise forms.ValidationError(
                _("Number already exists, numbers already used: %(number)s")
                % {"number": already_used}
            )
        return self.cleaned_data["number"]

    def _set_number_field_initial_value(self):
        value_max = self.signage.blade_set.all().aggregate(max=Max("number"))["max"]
        if settings.BLADE_CODE_TYPE is int:
            if not value_max:
                self.fields["number"].initial = "1"
            elif value_max.isdigit():
                self.fields["number"].initial = str(int(value_max) + 1)
        elif settings.BLADE_CODE_TYPE is str:
            if not value_max:
                self.fields["number"].initial = "A"
            elif len(value_max) == 1 and "A" <= value_max[0] < "Z":
                self.fields["number"].initial = chr(ord(value_max[0]) + 1)

    class Meta:
        model = Blade
        fields = ["id", "number", "direction", "type", "conditions", "color"]


class BladeForm(BaseBladeForm):
    # TODO: display uneditable map
    ...


if settings.TREKKING_TOPOLOGY_ENABLED:

    class BaseSignageForm(BaseInfrastructureForm):
        geomfields = ["topology"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            if not settings.SIGNAGE_LINE_ENABLED and settings.TREKKING_TOPOLOGY_ENABLED:
                modifiable = self.fields["topology"].widget.modifiable
                self.fields["topology"].widget = PointTopologyWidget()
                self.fields["topology"].widget.modifiable = modifiable
            self.helper.form_tag = False

else:

    class BaseSignageForm(BaseInfrastructureForm):
        geomfields = ["geom"]


class SignageForm(BaseSignageForm):
    fieldslayout = [
        Div(
            "structure",
            "name",
            "description",
            "type",
            "conditions",
            "implantation_year",
            "published",
            "code",
            "printed_elevation",
            "manager",
            "sealing",
            "access",
        )
    ]

    class Meta(BaseInfrastructureForm.Meta):
        model = Signage
        fields = [
            *BaseInfrastructureForm.Meta.fields,
            "code",
            "conditions",
            "printed_elevation",
            "manager",
            "sealing",
            "access",
        ]
