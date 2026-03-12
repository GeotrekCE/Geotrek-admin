from crispy_forms.layout import Div
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from geotrek.common.forms import CommonForm

from .models import Difficulty, Dive, Level


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


class DifficultyForm(forms.ModelForm):
    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get("id")

        exists = len(Difficulty.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(
                _("Difficulty with id '%s' already exists") % self.newid
            )
        return self.newid


class LevelForm(forms.ModelForm):
    def clean_id(self):
        self.oldid = self.instance.pk if self.instance else None
        self.newid = self.cleaned_data.get("id")

        exists = len(Level.objects.filter(pk=self.newid)) > 0
        if self.oldid != self.newid and exists:
            raise ValidationError(_("Level with id '%s' already exists") % self.newid)
        return self.newid
