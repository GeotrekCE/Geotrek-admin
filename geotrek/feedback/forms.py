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
