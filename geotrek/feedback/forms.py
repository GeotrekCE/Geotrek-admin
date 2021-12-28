from crispy_forms.layout import Div
from django.conf import settings
from django.forms.fields import CharField
from django.forms.widgets import HiddenInput, Textarea

from geotrek.authent.models import SelectableUser
from geotrek.common.forms import CommonForm
from .models import Report


class ReportForm(CommonForm):
    geomfields = ["geom"]

    class Meta:
        fields = [
            "geom",
            "email",
            "comment",
            "activity",
            "category",
            "problem_magnitude",
            "related_trek",
            "status",
            "locked",
            "uid",
            "origin"
        ]
        model = Report
