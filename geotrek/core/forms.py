from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout
from django import forms
from django.conf import settings
from django.contrib.gis.forms import LineStringField
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import MapWidget

from geotrek.common.forms import CommonForm

if settings.TREKKING_TOPOLOGY_ENABLED:
    from geotrek.core.mixins.forms import TopologyForm as BaseForm
else:
    from geotrek.common.forms import CommonForm as BaseForm
from geotrek.core.models import CertificationTrail, Path, Trail
from geotrek.core.widgets import LineTopologyWidget


class PathForm(CommonForm):
    reverse_geom = forms.BooleanField(
        required=False,
        label=_("Reverse path"),
        help_text=_("The path will be reversed once saved"),
    )

    geomfields = ["geom"]

    class Meta(CommonForm.Meta):
        model = Path
        widgets = {
            "geom": MapWidget(
                geom_type="LINESTRING",
                attrs={
                    "snapping_config": {
                        "enabled": True,
                        "layers": ["core.Path"],
                        "snap_distance": 20,
                    },
                },
            ),
        }
        fields = [
            *CommonForm.Meta.fields,
            "structure",
            "name",
            "stake",
            "comfort",
            "departure",
            "arrival",
            "comments",
            "source",
            "networks",
            "usages",
            "valid",
            "draft",
            "reverse_geom",
            "geom",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if not self.instance.draft:
                # Prevent to set a path as draft again (it could be used by a topology)
                del self.fields["draft"]
            if not self.user.has_perm("core.change_path"):
                del self.fields["draft"]
        else:
            if not self.user.has_perm("core.add_draft_path") or not self.user.has_perm(
                "core.add_path"
            ):
                del self.fields["draft"]
        self.fields["geom"].label = ""

    def clean_geom(self):
        pk = self.instance.pk if self.instance and self.instance.pk else -1
        geom = self.cleaned_data["geom"]
        if geom is None:
            raise forms.ValidationError(_("Invalid snapped geometry."))
        if not geom.simple:
            raise forms.ValidationError(_("Geometry is not simple."))
        if not Path.check_path_not_overlap(geom, pk):
            raise forms.ValidationError(_("Geometry overlaps another."))
        if not geom.valid:
            raise forms.ValidationError(_("Geometry is not valid."))
        return geom

    def save(self, commit=True):
        path = super().save(commit=False)
        if not self.instance.pk:
            if self.user.has_perm("core.add_draft_path") and not self.user.has_perm(
                "core.add_path"
            ):
                path.draft = True
            if not self.user.has_perm("core.add_draft_path") and self.user.has_perm(
                "core.add_path"
            ):
                path.draft = False

        if self.cleaned_data.get("reverse_geom"):
            path.reverse()

        if commit:
            path.save()
            self.save_m2m()

        return path


class TrailForm(BaseForm):
    fieldslayout = [
        Div(
            "structure",
            "name",
            "departure",
            "arrival",
            "category",
            "comments",
            Fieldset(_("Certifications")),
        )
    ]

    if settings.TREKKING_TOPOLOGY_ENABLED:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["topology"].widget.modifiable
            self.fields["topology"].widget = LineTopologyWidget()
            self.fields["topology"].widget.modifiable = modifiable
    else:
        geom = LineStringField()

    class Meta(BaseForm.Meta):
        model = Trail
        fields = [
            *BaseForm.Meta.fields,
            "structure",
            "name",
            "category",
            "departure",
            "arrival",
            "comments",
        ]
        if not settings.TREKKING_TOPOLOGY_ENABLED:
            fields.append("geom")


class CertificationTrailForm(forms.ModelForm):
    class Meta:
        model = CertificationTrail
        fields = ("id", "certification_label", "certification_status")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("id", "certification_label", "certification_status")


CertificationTrailFormSet = inlineformset_factory(
    Trail, CertificationTrail, form=CertificationTrailForm, extra=1
)
