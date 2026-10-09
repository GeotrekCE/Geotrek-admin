from django.db import models
from django.db.models.expressions import Exists, ExpressionWrapper, OuterRef
from django.db.models.query_utils import Q
from django.views.generic.dates import timezone_today

from geotrek.zoning.utils import weekday_between


def _period_ongoing_condition(today):
    ongoing = Q(start_date__lte=today) & (
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )
    return ongoing


def _period_finished_condition(today):
    finished = Q(end_date__lt=today)
    return finished


def _period_active_today_condition(today):
    active_today = (
        _period_ongoing_condition(today)
        & (Q(active_days=[]) | Q(active_days__contains=[today.weekday()]))
    )
    return active_today


class VigilancePeriodQuerySet(models.QuerySet):
    def ongoing(self):
        ongoing = _period_ongoing_condition(timezone_today())
        return self.filter(ongoing)

    def finished(self):
        finished = _period_finished_condition(timezone_today())
        return self.filter(finished)

    def active_today(self):
        active_today = _period_active_today_condition(timezone_today())
        return self.filter(active_today)


class VigilancePeriodManager(models.Manager.from_queryset(VigilancePeriodQuerySet)):
    def get_queryset(self):
        """
        # period_ongoing = boolean to define if a period is active (today in active period)
        # finished = boolean to define if a period is finished (today after end date)
        # active_today = boolean to define if the period is active today (active and day match)
        """
        today = timezone_today()
        qs = super().get_queryset()

        return qs.annotate(
            ongoing=ExpressionWrapper(
                _period_ongoing_condition(today), output_field=models.BooleanField()
            ),
            finished=ExpressionWrapper(
                _period_finished_condition(today), output_field=models.BooleanField()
            ),
            active_today=ExpressionWrapper(
                _period_active_today_condition(today),
                output_field=models.BooleanField(),
            ),
        )

    def ongoing(self):
        return self.get_queryset().ongoing()

    def finished(self):
        return self.get_queryset().finished()

    def active_today(self):
        return self.get_queryset().active_today()


class VigilanceAreaQuerySet(models.QuerySet):
    def _periods_exists(self, condition=None, negate=False):
        rel = self.model._meta.get_field("periods")
        periods = rel.related_model._base_manager.filter(
            **{rel.field.name: OuterRef("pk")}
        )
        if condition is not None:
            periods = periods.filter(condition)
        return ~Exists(periods) if negate else Exists(periods)

    def _no_periods(self):
        return self._periods_exists(negate=True)

    def _has_periods(self):
        return self._periods_exists()

    def _ongoing_expr(self, today):
        return (
            self._periods_exists(_period_ongoing_condition(today)) | self._no_periods()
        )

    def _finished_expr(self, today):
        not_finished = Q(end_date__isnull=True) | Q(end_date__gte=today)
        return self._periods_exists(not_finished, negate=True) & self._has_periods()

    def _active_today_expr(self, today):
        return (
            self._periods_exists(_period_active_today_condition(today))
            | self._no_periods()
        )

    def ongoing(self):
        return self.filter(self._ongoing_expr(timezone_today()))

    def finished(self):
        return self.filter(self._finished_expr(timezone_today()))

    def active_today(self):
        return self.filter(self._active_today_expr(timezone_today()))

    def active_by_dates(self, start=None, end=None):
        if start and end:
            period_active = Q(start_date__lte=end) & (
                Q(end_date__isnull=True) | Q(end_date__gte=start)
            )
            period_valid = (
                Q(active_days__len=0)
                | Q(active_days__overlap=weekday_between(start, end))
            )
            return self.filter(
                self._periods_exists(period_active & period_valid) | self._no_periods()
            )
        return self


class VigilanceAreaManager(models.Manager.from_queryset(VigilanceAreaQuerySet)):
    def get_queryset(self):
        """
        # ongoing = boolean to define if an area have an period in progress (today in active period)
        # finished = boolean to define if all the periods of an area are finished (today after end date)
        # active_today = boolean to define if an area have a period active today (active and day match)
        """
        today = timezone_today()
        qs = super().get_queryset()
        return qs.annotate(
            ongoing=qs._ongoing_expr(today),
            finished=qs._finished_expr(today),
            active_today=qs._active_today_expr(today),
        )

    def ongoing(self):
        return self.get_queryset().ongoing()

    def finished(self):
        return self.get_queryset().finished()

    def active_today(self):
        return self.get_queryset().active_today()
