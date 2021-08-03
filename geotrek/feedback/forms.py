from geotrek.common.forms import CommonForm
from .models import Report


class ReportForm(CommonForm):
    geomfields = ["geom"]

    class Meta:
        fields = [
            "geom",
            "email",
            "activity",
            "comment",
            "category",
            "problem_magnitude",
            "related_trek",
        ]
        model = Report
