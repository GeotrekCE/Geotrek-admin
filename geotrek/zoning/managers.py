from django.db import models
from django.db.models.expressions import Case, When
from django.db.models.query_utils import Q
from django.views.generic.dates import timezone_today


class VigilanceAreaManager(models.Manager):
    def active(self):
        qs = self.get_queryset()
        qs = qs.filter(period_active=True)
        return qs

    def finished(self):
        qs = self.get_queryset()
        qs = qs.filter(finished=True)
        return qs

    def active_by_date(self, start_date=None, end_date=None):
        qs = self.active()
        qs = (
            qs.filter(Q(end_date__isnull=True) | Q(end_date__gte=start_date))
            if start_date
            else qs
        )
        qs = qs.filter(Q(start_date__lte=end_date)) if end_date else qs
        return qs

    def get_queryset(self):
        qs = super().get_queryset()
        today = timezone_today()
        today_number = today.weekday()
        current_month_number = today.month

        # add boolean to define if period is active (today in active period)
        qs = qs.annotate(
            period_active=Case(
                When(start_date__lte=today, end_date__isnull=True, then=True),
                When(start_date__lte=today, end_date__gte=today, then=True),
                default=False,
                output_field=models.BooleanField(),
            )
        )
        # add boolean to define if period is finished (today after end date)
        qs = qs.annotate(
            finished=Case(
                When(end_date__isnull=False, end_date__lt=today, then=True),
                default=False,
                output_field=models.BooleanField(),
            )
        )
        # add boolean to define if active today (active and day and/or month match)
        qs = qs.annotate(
            active_today=Case(
                When(
                    Q(period_active=True)
                    & (Q(active_days=[]) | Q(active_days__contains=[today_number]))
                    & (
                        Q(active_months=[])
                        | Q(active_months__contains=[current_month_number])
                    ),
                    then=True,
                ),
                default=False,
                output_field=models.BooleanField(),
            ),
        )
        return qs
