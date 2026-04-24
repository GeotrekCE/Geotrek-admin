from copy import deepcopy

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout, Submit
from dal_select2.widgets import ModelSelect2Multiple
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from mapentity.forms import TranslatedModelForm
from mapentity.widgets import MapWidget, SelectMultipleWithPop
from modeltranslation.utils import build_localized_fieldname

from geotrek.common.forms import CommonForm
from geotrek.core.forms import TopologyForm
from geotrek.core.widgets import LineTopologyWidget, PointTopologyWidget

from .models import (
    POI,
    OrderedTrekChild,
    RatingScale,
    Service,
    ServiceType,
    Trek,
    WebLink,
)

if settings.TREKKING_TOPOLOGY_ENABLED:

    class BaseTrekForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["topology"].widget.modifiable
            # TODO: We should change LeafletWidget to keep modifiable.
            # Init of TopologyForm -> commonForm -> mapentityForm
            # already add a leafletwidget with modifiable
            self.fields["topology"].widget = LineTopologyWidget()
            self.fields["topology"].widget.modifiable = modifiable
            self.fields["points_reference"].label = ""
            self.fields["points_reference"].widget.target_map = "topology"
            self.fields["parking_location"].label = ""
            self.fields["parking_location"].widget.target_map = "topology"

        class Meta(TopologyForm.Meta):
            model = Trek
else:

    class BaseTrekForm(CommonForm):
        geomfields = ["geom"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["geom"].widget.modifiable
            self.fields["geom"].widget = MapWidget(attrs={"geom_type": "LINESTRING"})
            self.fields["geom"].widget.modifiable = modifiable
            self.fields["points_reference"].label = ""
            self.fields["points_reference"].widget.target_map = "geom"
            self.fields["parking_location"].label = ""
            self.fields["parking_location"].widget.target_map = "geom"

        class Meta(CommonForm.Meta):
            model = Trek
            fields = [*CommonForm.Meta.fields, "geom"]


class TrekForm(BaseTrekForm):
    children = forms.ModelMultipleChoiceField(
        queryset=Trek.objects.existing(), required=False, widget=ModelSelect2Multiple()
    )
    hidden_ordered_children = forms.CharField(
        label=_("Hidden ordered children"),
        widget=forms.widgets.HiddenInput(),
        required=False,
    )
    leftpanel_scrollable = False

    base_fieldslayout = [
        Div(
            HTML(
                """<ul class="nav nav-tabs">
    <li id="tab-main" class="nav-item">
        <a class="nav-link active" href="#main" data-toggle="tab"><i class="bi bi-card-list"></i> {}</a>
    </li>
    <li id="tab-advanced" class="nav-item">
        <a class="nav-link" href="#advanced" data-toggle="tab"><i class="bi bi-list-ul"></i> {}</a>
    </li>
    <li id="tab-accessibility" class="nav-item">
        <a class="nav-link" href="#accessibility" data-toggle="tab"><i class="bi bi-eye-slash-fill"></i> {}</a>
    </li>
</ul>""".format(_("Main"), _("Advanced"), _("Accessibility"))
            ),
            Div(
                Div(
                    "name",
                    "review",
                    "published",
                    "departure",
                    "arrival",
                    "duration",
                    "difficulty",
                    "practice",
                    "ratings_description",
                    "route",
                    "access",
                    "description_teaser",
                    "ambiance",
                    "description",
                    css_id="main",
                    css_class="scrollable tab-pane active",
                ),
                Div(
                    "points_reference",
                    "advised_parking",
                    "parking_location",
                    "public_transport",
                    "advice",
                    "gear",
                    "themes",
                    "labels",
                    "networks",
                    "web_links",
                    "information_desks",
                    "source",
                    "portal",
                    "children",
                    "hidden_ordered_children",
                    "eid",
                    "eid2",
                    "reservation_system",
                    "reservation_id",
                    "pois_excluded",
                    css_id="advanced",  # used in Javascript for activating tab if error
                    css_class="scrollable tab-pane",
                ),
                Div(
                    "accessibilities",
                    "accessibility_level",
                    "accessibility_infrastructure",
                    "accessibility_slope",
                    "accessibility_covering",
                    "accessibility_exposure",
                    "accessibility_width",
                    "accessibility_advice",
                    "accessibility_signage",
                    css_id="accessibility",  # used in Javascript for activating tab if error
                    css_class="scrollable tab-pane",
                ),
                css_class="tab-content",
            ),
            css_class="tabbable",
        ),
    ]

    def __init__(self, *args, **kwargs):
        # Store ordered_ids before calling super().__init__()
        self._ordered_children_ids = []
        self.fieldslayout = deepcopy(self.base_fieldslayout)
        service_types = ServiceType.objects.all()
        if any(st.pictogram for st in service_types):
            label = _("Insert service:")
            pictogram_links = "".join(
                [
                    f'<a class="servicetype" data-url="{t.pictogram.url}" data-name={t.name}">'
                    f'<img src="{t.pictogram.url}"></a>'
                    for t in service_types
                    if t.pictogram
                ]
            )
            self.fieldslayout[0][1][0].append(
                HTML(f'<div class="controls">{label}{pictogram_links}</div>')
            )
        super().__init__(*args, **kwargs)
        if self.fields.get("structure"):
            self.fieldslayout[0][1][0].insert(0, "structure")
        self.fields["web_links"].widget = SelectMultipleWithPop(
            choices=self.fields["web_links"].choices,
            add_url=WebLink.get_add_url(),
            attrs={
                "data-theme": "bootstrap4",
                "data-width": "75%",
            },
        )
        # Make sure (force) that name is required, in default language only
        self.fields[
            build_localized_fieldname("name", settings.LANGUAGE_CODE)
        ].required = True

        if not settings.TREK_POINTS_OF_REFERENCE_ENABLED:
            self.fields.pop("points_reference")
        else:
            # Edit points of reference with custom edition JavaScript class
            self.fields[
                "points_reference"
            ].widget.geometry_field_class = "PointsReferenceField"

        self.fields[
            "parking_location"
        ].widget.geometry_field_class = "ParkingLocationField"
        self.fields["duration"].widget.attrs["min"] = "0"

        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in [
            "themes",
            "networks",
            "accessibilities",
            "web_links",
            "information_desks",
            "source",
            "portal",
        ]:
            self.fields[f].help_text = ""

        if self.instance and self.instance.pk:
            queryset_children = OrderedTrekChild.objects.filter(
                parent__id=self.instance.pk
            ).order_by("order")
            ordered_children_ids = list(
                queryset_children.values_list("child__id", flat=True)
            )
            self._ordered_children_ids = ordered_children_ids

            # init multiple children field with data
            all_children = Trek.objects.existing().exclude(pk=self.instance.pk)

            # Set initial with ordered IDs
            self.fields["children"].initial = ordered_children_ids
            # init hidden field with children order
            self.fields["hidden_ordered_children"].initial = ",".join(
                str(x) for x in ordered_children_ids
            )

            # Force the queryset to render options in the correct order
            # by using Case/When to preserve the order
            if ordered_children_ids:
                from django.db.models import Case, IntegerField, Value, When

                preserved = Case(
                    *[
                        When(pk=pk, then=Value(i))
                        for i, pk in enumerate(ordered_children_ids)
                    ],
                    default=Value(len(ordered_children_ids) + 1),
                    output_field=IntegerField(),
                )

                self.fields["children"].queryset = all_children.annotate(
                    custom_order=preserved
                ).order_by("custom_order")
            else:
                self.fields["children"].queryset = all_children

        for scale in RatingScale.objects.all():
            ratings = None
            if self.instance.pk:
                ratings = self.instance.ratings.filter(scale=scale)
            fieldname = f"rating_scale_{scale.pk}"
            self.fields[fieldname] = forms.ModelChoiceField(
                label=scale.name,
                queryset=scale.ratings.all(),
                required=False,
                initial=ratings[0] if ratings else None,
            )
            right_after_type_index = (
                self.fieldslayout[0][1][0].fields.index("practice") + 1
            )
            self.fieldslayout[0][1][0].insert(right_after_type_index, fieldname)

        if self.instance.pk:
            self.fields["pois_excluded"].queryset = self.instance.all_pois.all()
        else:
            self.fieldslayout[0][1][1].remove("pois_excluded")

    def clean(self):
        cleaned_data = super().clean()
        practice = self.cleaned_data["practice"]
        for scale in RatingScale.objects.all():
            if self.cleaned_data.get(f"rating_scale_{scale.pk}"):
                try:
                    practice.rating_scales.get(pk=scale.pk)
                except RatingScale.DoesNotExist:
                    raise ValidationError(
                        _(
                            "One of the rating scale used is not part of the practice chosen"
                        )
                    )
        return cleaned_data

    def clean_children(self):
        """
        Check the trek is not parent and child at the same time
        """
        children = self.cleaned_data["children"]
        if (
            children
            and self.instance
            and self.instance.pk
            and self.instance.trek_parents.exists()
        ):
            raise ValidationError(
                _("Cannot add children because this trek is itself a child.")
            )
        for child in children:
            if child.trek_children.exists():
                raise ValidationError(
                    _("Cannot use parent trek %(name)s as a child trek.")
                    % {"name": child.name}
                )
        return children

    def save(self, commit=True):
        """
        Custom form save override - ordered children management
        """
        instance = super().save(commit=commit)

        # Django contract: when commit=False, caller is responsible for saving
        # instance and then calling form.save_m2m().
        if not commit:
            return instance

        # Related updates require a persisted instance.
        with transaction.atomic():
            # Save ratings
            # TODO : Go through practice and not rating_scales
            if instance.practice:
                field = getattr(instance, "ratings")
                to_remove = list(
                    field.exclude(scale__practice=instance.practice).values_list(
                        "pk", flat=True
                    )
                )
                to_add = []
                for scale in instance.practice.rating_scales.all():
                    rating = self.cleaned_data.get(f"rating_scale_{scale.pk}")
                    needs_removal = field.filter(scale=scale)
                    if rating:
                        needs_removal = needs_removal.exclude(pk=rating.pk)
                        to_add.append(rating.pk)
                    to_remove += list(needs_removal.values_list("pk", flat=True))
                field.remove(*to_remove)
                field.add(*to_add)

            # Save ordered children links only (do not delete Trek objects)
            selected_children = list(self.cleaned_data.get("children") or [])
            selected_ids = [child.pk for child in selected_children]
            ordered_ids = []

            raw_ordering = self.cleaned_data.get("hidden_ordered_children", "")
            if raw_ordering:
                for value in raw_ordering.split(","):
                    value = value.strip()
                    if not value:
                        continue
                    try:
                        child_id = int(value)
                    except ValueError:
                        continue
                    if child_id in selected_ids and child_id not in ordered_ids:
                        ordered_ids.append(child_id)

            # Keep selected items even if they were not present in the hidden order.
            for child_id in selected_ids:
                if child_id not in ordered_ids:
                    ordered_ids.append(child_id)

            instance.trek_children.all().delete()
            for order, child_id in enumerate(ordered_ids):
                OrderedTrekChild.objects.create(
                    parent=instance,
                    child_id=child_id,
                    order=order,
                )

        return instance

    class Meta(BaseTrekForm.Meta):
        fields = [
            *BaseTrekForm.Meta.fields,
            "structure",
            "name",
            "review",
            "published",
            "labels",
            "departure",
            "arrival",
            "duration",
            "difficulty",
            "route",
            "ambiance",
            "access",
            "description_teaser",
            "description",
            "ratings_description",
            "points_reference",
            "accessibility_infrastructure",
            "advised_parking",
            "parking_location",
            "public_transport",
            "advice",
            "gear",
            "themes",
            "networks",
            "practice",
            "accessibilities",
            "accessibility_level",
            "accessibility_signage",
            "accessibility_slope",
            "accessibility_covering",
            "accessibility_exposure",
            "accessibility_width",
            "accessibility_advice",
            "web_links",
            "information_desks",
            "source",
            "portal",
            "children",
            "hidden_ordered_children",
            "eid",
            "eid2",
            "reservation_system",
            "reservation_id",
            "pois_excluded",
        ]


if settings.TREKKING_TOPOLOGY_ENABLED:

    class BasePOIForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["topology"].widget.modifiable
            self.fields["topology"].widget = PointTopologyWidget()
            self.fields["topology"].widget.modifiable = modifiable

        class Meta(TopologyForm.Meta):
            model = POI

else:

    class BasePOIForm(CommonForm):
        geomfields = ["geom"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["geom"].widget.modifiable
            self.fields["geom"].widget = MapWidget(attrs={"geom_type": "POINT"})
            self.fields["geom"].widget.modifiable = modifiable

        class Meta(CommonForm.Meta):
            model = POI
            fields = [*CommonForm.Meta.fields, "geom"]


class POIForm(BasePOIForm):
    fieldslayout = [
        Div(
            "structure",
            "name",
            "review",
            "published",
            "type",
            "description",
            "eid",
        )
    ]

    class Meta(BasePOIForm.Meta):
        fields = [
            *BasePOIForm.Meta.fields,
            "structure",
            "name",
            "description",
            "eid",
            "type",
            "published",
            "review",
        ]


if settings.TREKKING_TOPOLOGY_ENABLED:

    class BaseServiceForm(TopologyForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["topology"].widget.modifiable
            self.fields["topology"].widget = PointTopologyWidget()
            self.fields["topology"].widget.modifiable = modifiable

        class Meta(TopologyForm.Meta):
            model = Service

else:

    class BaseServiceForm(CommonForm):
        geomfields = ["geom"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            modifiable = self.fields["geom"].widget.modifiable
            self.fields["geom"].widget = MapWidget(attrs={"geom_type": "POINT"})
            self.fields["geom"].widget.modifiable = modifiable

        class Meta(CommonForm.Meta):
            model = Service
            fields = [*CommonForm.Meta.fields, "geom"]


class ServiceForm(BaseServiceForm):
    fieldslayout = [
        Div(
            "structure",
            "type",
            "eid",
        )
    ]

    class Meta(BaseServiceForm.Meta):
        fields = [*BaseServiceForm.Meta.fields, "structure", "type", "eid"]


class WebLinkCreateFormPopup(TranslatedModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = self.instance.get_add_url()
        # Main form layout
        # Adds every name field explicitly (name_fr, name_en, ...)
        self.helper.form_class = "form-horizontal"
        arg_list = [
            build_localized_fieldname("name", language[0])
            for language in settings.MAPENTITY_CONFIG["TRANSLATED_LANGUAGES"]
        ]
        arg_list += [
            "url",
            "category",
            FormActions(
                HTML(
                    '<a href="#" class="btn" onclick="javascript:window.close();">{}</a>'.format(
                        _("Cancel")
                    )
                ),
                Submit("save_changes", _("Create"), css_class="btn-primary"),
                css_class="form-actions",
            ),
        ]
        self.helper.layout = Layout(*arg_list)

    class Meta:
        model = WebLink
        fields = ["name", "url", "category"]
