from django_filters.widgets import RangeWidget


class OneLineRangeWidget(RangeWidget):
    template_name = "common/range_widget.html"
