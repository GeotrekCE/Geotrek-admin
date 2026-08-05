import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields.array import ArrayField
from django.contrib.postgres.indexes import GinIndex, GistIndex
from django.core.exceptions import ValidationError
from django.db.models import Index
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _
from django.views.generic.dates import timezone_today

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (
    BBoxMixin,
    ExternalSourceMixin,
    GeotrekMapEntityMixin,
    OptionalPictogramMixin,
    PicturesMixin,
    PublishableMixin,
    TimeStampedModelMixin,
)

from ..common.functions import GenRandomUUID
from .choices import MonthChoices, Practicability, WeekdayChoices
from .managers import VigilanceAreaManager


class RestrictedAreaType(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Restricted area type")

    def __str__(self):
        return self.name


class RestrictedArea(TimeStampedModelMixin, BBoxMixin, models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"), db_index=True)
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    area_type = models.ForeignKey(
        RestrictedAreaType, verbose_name=_("Restricted area"), on_delete=models.PROTECT
    )
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=True,
        help_text=_("Visible on Geotrek-rando"),
    )

    @classmethod
    def latest_updated(cls, type_id=None):
        try:
            qs = cls.objects.all()
            if type_id:
                qs = cls.objects.filter(area_type_id=type_id)
            return qs.only("date_update").latest("date_update").date_update
        except cls.DoesNotExist:
            return None

    class Meta:
        ordering = ["area_type", "name"]
        verbose_name = _("Restricted area")
        verbose_name_plural = _("Restricted areas")
        indexes = [
            GistIndex(name="restrictedarea_geom_gist_idx", fields=["geom"]),
            Index(name="restrictedarea_type_name_idx", fields=["area_type_id", "name"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
        ]

    def __str__(self):
        return f"{self.area_type.name} - {self.name}"


class City(TimeStampedModelMixin, BBoxMixin, models.Model):
    code = models.CharField(
        max_length=256,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Code"),
        db_index=True,
    )
    name = models.CharField(max_length=128, verbose_name=_("Name"), db_index=True)
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=True,
        help_text=_("Visible on Geotrek-rando"),
    )

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ["name"]
        indexes = [
            GistIndex(name="city_geom_gist_idx", fields=["geom"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
        ]

    def __str__(self):
        return self.name


class District(TimeStampedModelMixin, BBoxMixin, models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Name"), db_index=True)
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=True,
        help_text=_("Visible on Geotrek-rando"),
    )

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        ordering = ["name"]
        indexes = [
            GistIndex(name="district_geom_gist_idx", fields=["geom"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
        ]

    def __str__(self):
        return self.name


class VigilanceAreaType(OptionalPictogramMixin, TimeStampedModelMixin, models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Vigilance area type")
        verbose_name_plural = _("Vigilance area types")

    def __str__(self):
        return self.name


class VigilanceArea(
    TimeStampedModelMixin,
    StructureRelated,
    PublishableMixin,
    GeotrekMapEntityMixin,
    ExternalSourceMixin,
    PicturesMixin,
    models.Model,
):
    name = models.CharField(max_length=250, verbose_name=_("Name"), db_index=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    start_date = models.DateField(
        verbose_name=_("Start date"),
        default=timezone_today,
        db_default=Now(),
        db_index=True,
    )
    end_date = models.DateField(
        verbose_name=_("End date"), blank=True, null=True, db_index=True
    )
    practicability = models.CharField(
        verbose_name=_("Practicability"),
        choices=Practicability.choices,
        max_length=50,
        default=Practicability.PRACTICABLE,
        db_index=True,
    )
    vigilance_area_type = models.ForeignKey(
        VigilanceAreaType,
        on_delete=models.CASCADE,
        verbose_name=_("Type"),
        related_name="vigilance_areas",
    )
    practical_info = models.TextField(
        verbose_name=_("Practical information"), blank=True
    )
    external_info_url = models.URLField(
        verbose_name=_("External information URL"), blank=True, default=""
    )
    portals = models.ManyToManyField(
        "common.TargetPortal",
        blank=True,
        related_name="vigilance_areas",
        verbose_name=_("Portals"),
    )
    sources = models.ManyToManyField(
        "common.RecordSource",
        blank=True,
        related_name="vigilance_areas",
        verbose_name=_("Sources"),
    )
    active_days = ArrayField(
        models.IntegerField(
            choices=WeekdayChoices.choices,
        ),
        verbose_name=_("Active days"),
        help_text=_(
            "Days of the week when the vigilance area is active. Empty equals all week."
        ),
        default=list,
        blank=True,
    )
    active_months = ArrayField(
        models.IntegerField(
            choices=MonthChoices.choices,
        ),
        verbose_name=_("Active months"),
        default=list,
        help_text=_(
            "Months of the year when the vigilance area is active. Empty equals all year."
        ),
        blank=True,
    )
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_default=GenRandomUUID()
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({"start_date": _("Start date is after end date")})

    @property
    def active_days_labels(self):
        # Mapping des entiers vers les labels textuels
        choices_map = dict(WeekdayChoices.choices)
        return [choices_map.get(day) for day in self.active_days]

    @property
    def active_months_labels(self):
        choices_map = dict(MonthChoices.choices)
        return [choices_map.get(month) for month in self.active_months]

    @property
    def period_active_verbose_name(self):
        return _("Period active")

    @property
    def active_today_verbose_name(self):
        return _("Active today")

    @property
    def period_resume(self):
        if self.end_date:
            result = _("From %s to %s") % (self.start_date, self.end_date)
        else:
            result = _("From %s") % self.start_date

        if self.active_days:
            result += _(" - days %s") % (",".join(self.active_days_labels))
        if self.active_months:
            result += _(" - months %s") % (",".join(self.active_months_labels))
        return result

    objects = VigilanceAreaManager()

    class Meta:
        verbose_name = _("Vigilance area")
        verbose_name_plural = _("Vigilance areas")
        ordering = ["name"]
        indexes = [
            GistIndex(name="vigilance_area_geom_gist_idx", fields=["geom"]),
            GinIndex(name="va_active_days_gin_idx", fields=["active_days"]),
            GinIndex(
                name="va_active_months_gin_idx",
                fields=["active_months"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
            models.CheckConstraint(
                check=models.Q(practicability__in=Practicability.values),
                name="%(app_label)s_%(class)s_practicability_valid",
            ),
        ]
