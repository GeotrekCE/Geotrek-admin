from crispy_forms.layout import Div

from geotrek.common.forms import CommonForm

from .models import Dive


class DiveForm(CommonForm):
    geomfields = ["geom"]

    fieldslayout = [
        Div(
            "structure",
            "name",
            "practice",
            "review",
            "published",
            "description_teaser",
            "description",
            "advice",
            "difficulty",
            "levels",
            "themes",
            "owner",
            "depth",
            "facilities",
            "departure",
            "disabled_sport",
            "source",
            "portal",
            "eid",
        )
    ]

    class Meta:
        fields = [
            "structure",
            "name",
            "practice",
            "review",
            "published",
            "description_teaser",
            "description",
            "advice",
            "difficulty",
            "levels",
            "themes",
            "owner",
            "depth",
            "facilities",
            "departure",
            "disabled_sport",
            "source",
            "portal",
            "geom",
            "eid",
        ]
        model = Dive

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ["themes", "levels", "source", "portal"]:
            self.fields[f].help_text = ""
