"""

Zoning models
(not MapEntity : just layers, on which intersections with objects is done in triggers)

"""

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.indexes import GistIndex
from django.utils.translation import gettext_lazy as _

from geotrek.common.mixins.models import TimeStampedModelMixin


class RestrictedAreaType(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Restricted area type")

    def __str__(self):
        return self.name


class RestrictedArea(TimeStampedModelMixin, models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    area_type = models.ForeignKey(
        RestrictedAreaType, verbose_name=_("Restricted area"), on_delete=models.PROTECT
    )
    published = models.BooleanField(
        verbose_name=_("Published"),
        default=True,
        help_text=_("Visible on Geotrek-rando"),
    )

    class Meta:
        ordering = ["area_type", "name"]
        verbose_name = _("Restricted area")
        verbose_name_plural = _("Restricted areas")
        indexes = [
            GistIndex(name="restrictedarea_geom_gist_idx", fields=["geom"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(geom__isvalid=True),
                name="%(app_label)s_%(class)s_geom_is_valid",
            ),
        ]

    def __str__(self):
        return f"{self.area_type.name} - {self.name}"


class City(TimeStampedModelMixin, models.Model):
    code = models.CharField(max_length=6, null=True)
    name = models.CharField(max_length=128, verbose_name=_("Name"))
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


class District(TimeStampedModelMixin, models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
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
