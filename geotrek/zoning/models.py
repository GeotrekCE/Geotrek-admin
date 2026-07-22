from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db.models import Index
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (
    BBoxMixin,
    ExternalSourceMixin,
    GeotrekMapEntityMixin,
    PictogramMixin,
    PicturesMixin,
    PublishableMixin,
    TimeStampedModelMixin,
)

from .choices import Practicability


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


class VigilanceAreaType(PictogramMixin, models.Model):
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
    start_date = models.DateField(verbose_name=_("Start date"), default=now)
    end_date = models.DateField(verbose_name=_("End date"), blank=True, null=True)
    practicability = models.CharField(
        verbose_name=_("Practicability"),
        choices=Practicability.choices,
        max_length=50,
        default=Practicability.PRACTICABLE,
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
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError({"start_date": _("Start date is after end date")})

    class Meta:
        verbose_name = _("Vigilance area")
        verbose_name_plural = _("Vigilance areas")
        ordering = ["name"]
        indexes = [
            GistIndex(name="vigilance_area_geom_gist_idx", fields=["geom"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
        ]
