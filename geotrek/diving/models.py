from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.gis.db import models
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (
    AddPropertyMixin,
    GeotrekMapEntityMixin,
    NoDeleteMixin,
    OptionalPictogramMixin,
    PictogramMixin,
    PicturesMixin,
    PublishableMixin,
    TimeStampedModelMixin,
    get_uuid_duplication,
)
from geotrek.common.models import Theme
from geotrek.common.utils import format_coordinates, intersecting, spatial_reference
from geotrek.core.models import Topology
from geotrek.trekking.models import POI, Service, Trek
from geotrek.zoning.mixins import ZoningPropertiesMixin


class Practice(TimeStampedModelMixin, PictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    order = models.IntegerField(
        verbose_name=_("Order"),
        null=True,
        blank=True,
        help_text=_("Alphabetical order if blank"),
    )
    color = ColorField(
        verbose_name=_("Color"),
        default="#444444",
        help_text=_("Color of the practice, only used in mobile."),
    )  # To be implemented in Geotrek-rando

    id_prefix = "D"

    class Meta:
        verbose_name = _("Practice")
        verbose_name_plural = _("Practices")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Difficulty(OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order difficulty levels, especially in public website
    where treks are filtered by difficulty ids.
    """

    id = models.IntegerField(primary_key=True, verbose_name=_("Order"))
    name = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Difficulty level")
        verbose_name_plural = _("Difficulty levels")
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by("-id")[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super().save(*args, **kwargs)


class Level(OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order technical levels, especially in public website
    where treks are filtered by level ids.
    """

    id = models.IntegerField(primary_key=True, verbose_name=_("Order"))
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    description = models.TextField(
        verbose_name=_("Description"), blank=True, help_text=_("Complete description")
    )

    class Meta:
        verbose_name = _("Technical level")
        verbose_name_plural = _("Technical levels")
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by("-id")[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super().save(*args, **kwargs)


class Dive(
    ZoningPropertiesMixin,
    NoDeleteMixin,
    AddPropertyMixin,
    PublishableMixin,
    GeotrekMapEntityMixin,
    StructureRelated,
    TimeStampedModelMixin,
    PicturesMixin,
):
    description_teaser = models.TextField(
        verbose_name=_("Description teaser"), blank=True, help_text=_("A brief summary")
    )
    description = models.TextField(
        verbose_name=_("Description"), blank=True, help_text=_("Complete description")
    )
    owner = models.CharField(verbose_name=_("Owner"), max_length=256, blank=True)
    practice = models.ForeignKey(
        Practice,
        related_name="dives",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Practice"),
    )
    departure = models.CharField(
        verbose_name=_("Departure area"), max_length=128, blank=True
    )
    disabled_sport = models.TextField(
        verbose_name=_("Disabled sport accessibility"), blank=True
    )
    facilities = models.TextField(verbose_name=_("Facilities"), blank=True)
    difficulty = models.ForeignKey(
        Difficulty,
        related_name="dives",
        blank=True,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_("Difficulty level"),
    )
    levels = models.ManyToManyField(
        Level, related_name="dives", blank=True, verbose_name=_("Technical levels")
    )
    depth = models.PositiveIntegerField(
        verbose_name=_("Maximum depth"), blank=True, null=True, help_text=_("meters")
    )
    advice = models.TextField(
        verbose_name=_("Advice"),
        blank=True,
        help_text=_("Risks, danger, best period, ..."),
    )
    themes = models.ManyToManyField(
        Theme,
        related_name="dives",
        blank=True,
        verbose_name=_("Themes"),
        help_text=_("Main theme(s)"),
    )
    geom = models.GeometryField(verbose_name=_("Location"), srid=settings.SRID)
    source = models.ManyToManyField(
        "common.RecordSource",
        blank=True,
        related_name="dives",
        verbose_name=_("Source"),
    )
    portal = models.ManyToManyField(
        "common.TargetPortal",
        blank=True,
        related_name="dives",
        verbose_name=_("Portal"),
    )
    eid = models.CharField(
        verbose_name=_("External id"), max_length=1024, blank=True, null=True
    )

    elements_duplication = {"attachments": {"uuid": get_uuid_duplication}}

    class Meta:
        verbose_name = _("Dive")
        verbose_name_plural = _("Dives")

    def __str__(self):
        return self.name

    @property
    def display_geom(self):
        return "{} ({})".format(format_coordinates(self.geom), spatial_reference())

    def distance(self, to_cls):
        return settings.DIVING_INTERSECTION_MARGIN

    def get_map_image_url(self):
        return reverse("diving:dive_map_image", args=[str(self.pk), get_language()])

    @classmethod
    def get_create_label(cls):
        return _("Add a new dive")

    @property
    def levels_display(self):
        return ", ".join([str(level) for level in self.levels.all()])


Topology.add_property("dives", lambda self: intersecting(Dive, self), _("Dives"))
Topology.add_property(
    "published_dives",
    lambda self: intersecting(Dive, self).filter(published=True),
    _("Published dives"),
)
Dive.add_property("dives", lambda self: intersecting(Dive, self), _("Dives"))
Dive.add_property(
    "published_dives",
    lambda self: intersecting(Dive, self).filter(published=True),
    _("Published dives"),
)
Dive.add_property("treks", lambda self: intersecting(Trek, self), _("Treks"))
Dive.add_property(
    "published_treks",
    lambda self: intersecting(Trek, self).filter(published=True),
    _("Published treks"),
)

Dive.add_property("pois", lambda self: intersecting(POI, self), _("POIs"))
Dive.add_property(
    "published_pois",
    lambda self: intersecting(POI, self).filter(published=True),
    _("Published POIs"),
)

Dive.add_property("services", lambda self: intersecting(Service, self), _("Services"))
Dive.add_property(
    "published_services",
    lambda self: intersecting(Service, self).filter(published=True),
    _("Published Services"),
)

if "geotrek.tourism" in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    tourism_models.TouristicContent.add_property(
        "dives", lambda self: intersecting(Dive, self), _("Dives")
    )
    tourism_models.TouristicContent.add_property(
        "published_dives",
        lambda self: intersecting(Dive, self).filter(published=True),
        _("Published dives"),
    )
    tourism_models.TouristicEvent.add_property(
        "dives", lambda self: intersecting(Dive, self), _("Dives")
    )
    tourism_models.TouristicEvent.add_property(
        "published_dives",
        lambda self: intersecting(Dive, self).filter(published=True),
        _("Published dives"),
    )

    Dive.add_property(
        "touristic_contents",
        lambda self: intersecting(tourism_models.TouristicContent, self),
        _("Touristic contents"),
    )
    Dive.add_property(
        "published_touristic_contents",
        lambda self: intersecting(tourism_models.TouristicContent, self).filter(
            published=True
        ),
        _("Published touristic contents"),
    )
    Dive.add_property(
        "touristic_events",
        lambda self: intersecting(tourism_models.TouristicEvent, self),
        _("Touristic events"),
    )
    Dive.add_property(
        "published_touristic_events",
        lambda self: intersecting(tourism_models.TouristicEvent, self).filter(
            published=True
        ),
        _("Published touristic events"),
    )
