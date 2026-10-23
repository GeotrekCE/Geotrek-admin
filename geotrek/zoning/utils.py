from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def weekday_between(start_date, end_date):
    if start_date is None or end_date is None:
        msg = _("start date and end date of the period must be configured")
        raise ValidationError(msg)

    try:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        msg = _("Date must have format YYYY-MM-DD")
        raise ValueError(msg) from e

    nb_days = min((end_date - start_date).days + 1, 7)
    return [(start_date.weekday() + i) % 7 for i in range(nb_days)]
