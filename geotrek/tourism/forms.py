from datetime import datetime

from crispy_forms.layout import HTML, Div, Fieldset
from django.utils.translation import gettext_lazy as _
from mapentity.widgets import SelectMultipleWithPop

from geotrek.common.forms import CommonForm
from geotrek.tourism.widgets import AutoLocateMapWidget

from .models import (
    TouristicContent,
    TouristicEvent,
    TouristicEventOrganizer,
    TouristicEventParticipantCategory,
    TouristicEventParticipantCount,
)


class TouristicContentForm(CommonForm):
    geomfields = ["geom"]

    fieldslayout = [
        Div(
            "structure",
            "name",
            "category",
            "type1",
            "type2",
            "review",
            "published",
            "approved",
            "description_teaser",
            "description",
            "themes",
            "contact",
            "email",
            "website",
            "practical_info",
            "accessibility",
            "label_accessibility",
            "source",
            "portal",
            "eid",
            "reservation_system",
            "reservation_id",
        )
    ]

    class Meta:
        fields = [
            "structure",
            "name",
            "category",
            "type1",
            "type2",
            "review",
            "published",
            "description_teaser",
            "description",
            "themes",
            "contact",
            "email",
            "website",
            "practical_info",
            "accessibility",
            "label_accessibility",
            "approved",
            "source",
            "portal",
            "geom",
            "eid",
            "reservation_system",
            "reservation_id",
        ]
        model = TouristicContent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ["themes", "type1", "type2", "source", "portal"]:
            self.fields[f].help_text = ""


class TouristicEventForm(CommonForm):
    geomfields = ["geom"]
    leftpanel_scrollable = False

    fieldslayout = [
        Div(
            HTML(
                """<ul class="nav nav-tabs">
    <li id="tab-event" class="nav-item">
        <a class="nav-link active" href="#event" data-toggle="tab"><i class="bi bi-card-list"></i> {0}</a>
    </li>
    <li id="tab-assessment" class="nav-item">
        <a class="nav-link" href="#assessment" data-toggle="tab"><i class="bi bi-list-ul"></i> {1}</a>
    </li>
</ul>""".format(_("Event"), _("Assessment"))
            ),
            Div(
                Div(
                    "structure",
                    "name",
                    "review",
                    "published",
                    "approved",
                    "type",
                    "themes",
                    "begin_date",
                    "end_date",
                    "start_time",
                    "end_time",
                    "duration",
                    "price",
                    "place",
                    "meeting_point",
                    "description_teaser",
                    "description",
                    "target_audience",
                    "practical_info",
                    "contact",
                    "email",
                    "website",
                    "organizers",
                    "speaker",
                    "accessibility",
                    "bookable",
                    Div("booking", css_id="booking_widget"),
                    "capacity",
                    "cancelled",
                    "cancellation_reason",
                    "source",
                    "portal",
                    "eid",
                    css_id="event",
                    css_class="scrollable tab-pane active",
                ),
                Div(
                    Fieldset(
                        _("Participants"),
                    ),
                    HTML("<hr>"),
                    "preparation_duration",
                    "intervention_duration",
                    css_id="assessment",
                    css_class="scrollable tab-pane",
                ),
                css_class="tab-content",
            ),
            css_class="tabbable",
        ),
    ]

    class Meta:
        fields = [
            "name",
            "place",
            "review",
            "published",
            "description_teaser",
            "description",
            "themes",
            "begin_date",
            "end_date",
            "duration",
            "meeting_point",
            "start_time",
            "end_time",
            "contact",
            "email",
            "website",
            "organizers",
            "speaker",
            "type",
            "accessibility",
            "capacity",
            "booking",
            "target_audience",
            "practical_info",
            "approved",
            "source",
            "portal",
            "geom",
            "eid",
            "structure",
            "bookable",
            "cancelled",
            "cancellation_reason",
            "preparation_duration",
            "intervention_duration",
            "price",
        ]
        model = TouristicEvent
        widgets = {"geom": AutoLocateMapWidget()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["begin_date"].widget.attrs["placeholder"] = _("dd/mm/yyyy")
        self.fields["end_date"].widget.attrs["placeholder"] = _("dd/mm/yyyy")
        self.fields["start_time"].widget.attrs["placeholder"] = _("HH:MM")
        self.fields["end_time"].widget.attrs["placeholder"] = _("HH:MM")
        if self.user.has_perm("tourism.add_touristiceventorganizer"):
            self.fields["organizers"].widget = SelectMultipleWithPop(
                choices=self.fields["organizers"].choices,
                add_url=TouristicEventOrganizer.get_add_url(),
            )
        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ["themes", "source"]:
            self.fields[f].help_text = ""
        participants_count = {}
        if self.instance and self.instance.pk:
            participants_count = {
                p.category.pk: p.count
                for p in self.instance.participants.select_related("category").all()
            }
        categories = TouristicEventParticipantCategory.objects.all()
        if not categories:
            self.fieldslayout[0][1][1][0].append(
                HTML(
                    _(
                        "Please add a participant category in admin interface in order to complete the number of participants."
                    )
                )
            )
        else:
            for category in categories:
                field_id = f"participant_count_{category.id}"
                self.fields[field_id] = TouristicEventParticipantCount._meta.get_field(
                    "count"
                ).formfield(required=False)
                self.fields[field_id].label = category.label
                self.fields[field_id].initial = participants_count.get(category.pk)
                self.fieldslayout[0][1][1][0].append(field_id)

    def clean(self, *args, **kwargs):
        clean_data = super().clean(*args, **kwargs)
        start_time = clean_data.get("start_time")
        end_time = clean_data.get("end_time")
        if not start_time and not end_time:
            pass
        elif not start_time and end_time:
            self.add_error("start_time", _("Start time is unset"))
        elif not end_time:
            pass
        elif not clean_data.get("end_date"):
            if start_time > end_time:
                self.add_error("end_time", _("Start time is after end time"))
        else:
            begin = datetime.combine(clean_data.get("begin_date"), start_time)
            end = datetime.combine(clean_data.get("end_date"), end_time)
            if begin > end:
                self.add_error("end_time", _("Start time is after end time"))

        if clean_data.get("end_date") and clean_data.get("end_date") < clean_data.get(
            "begin_date"
        ):
            self.add_error("end_date", _("Start date is after end date"))

        return clean_data

    def _save_m2m(self):
        super()._save_m2m()
        for category in TouristicEventParticipantCategory.objects.all():
            count = self.cleaned_data[f"participant_count_{category.id}"]
            if count is not None:
                TouristicEventParticipantCount.objects.update_or_create(
                    event=self.instance, category=category, defaults={"count": count}
                )
            else:
                TouristicEventParticipantCount.objects.filter(
                    event=self.instance, category=category
                ).delete()


class TouristicEventOrganizerFormPopup(CommonForm):
    class Meta:
        model = TouristicEventOrganizer
        fields = ["label"]
