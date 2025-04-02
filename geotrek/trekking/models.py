import logging
import os

import simplekml
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import LineLocatePoint, Transform
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import F
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import get_language, gettext
from django.utils.translation import gettext_lazy as _
from mapentity.helpers import clone_attachment
from mapentity.serializers import plain_text

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (
    BasePublishableMixin,
    GeotrekMapEntityMixin,
    OptionalPictogramMixin,
    PictogramMixin,
    PicturesMixin,
    PublishableMixin,
    TimeStampedModelMixin,
    get_uuid_duplication,
)
from geotrek.common.models import (
    AccessibilityAttachment,
    RatingMixin,
    RatingScaleMixin,
    ReservationSystem,
    Theme,
)
from geotrek.common.signals import log_cascade_deletion
from geotrek.common.templatetags import geotrek_tags
from geotrek.common.utils import (
    classproperty,
    intersecting,
    queryset_or_all_objects,
    queryset_or_model,
)
from geotrek.core.models import Path, Topology, simplify_coords
from geotrek.maintenance.models import Intervention, Project
from geotrek.tourism import models as tourism_models
from geotrek.trekking.managers import (
    POIManager,
    ServiceManager,
    TrekManager,
    TrekOrderedChildManager,
    WebLinkManager,
)

logger = logging.getLogger(__name__)


if "geotrek.signage" in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade


class OrderedTrekChild(models.Model):
    parent = models.ForeignKey(
        "Trek", related_name="trek_children", on_delete=models.CASCADE
    )
    child = models.ForeignKey(
        "Trek", related_name="trek_parents", on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    objects = TrekOrderedChildManager()

    class Meta:
        ordering = ("parent__id", "order")
        unique_together = (("parent", "child"),)


class Practice(TimeStampedModelMixin, PictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    distance = models.IntegerField(
        verbose_name=_("Distance"),
        blank=True,
        null=True,
        help_text=_(
            "Touristic contents and events will associate within this distance (meters)"
        ),
    )
    cirkwi = models.ForeignKey(
        "cirkwi.CirkwiLocomotion",
        verbose_name=_("Cirkwi locomotion"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
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

    id_prefix = "T"

    class Meta:
        verbose_name = _("Practice")
        verbose_name_plural = _("Practices")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name) or str(self.pk)


class RatingScale(RatingScaleMixin):
    practice = models.ForeignKey(
        Practice,
        related_name="rating_scales",
        on_delete=models.CASCADE,
        verbose_name=_("Practice"),
    )

    class Meta:
        verbose_name = _("Rating scale")
        verbose_name_plural = _("Rating scales")
        ordering = ("practice", "order", "name")


@receiver(pre_delete, sender=Practice)
def log_cascade_deletion_from_practice(sender, instance, using, **kwargs):
    # RatingScale are deleted when Practices are deleted
    log_cascade_deletion(sender, instance, RatingScale, "practice")


class Rating(RatingMixin):
    scale = models.ForeignKey(
        RatingScale,
        related_name="ratings",
        on_delete=models.CASCADE,
        verbose_name=_("Scale"),
    )

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")
        ordering = ("order", "name")


@receiver(pre_delete, sender=RatingScale)
def log_cascade_deletion_from_rating_scale(sender, instance, using, **kwargs):
    # Ratings are deleted when RatingScales are deleted
    log_cascade_deletion(sender, instance, Rating, "scale")


class Trek(
    Topology, StructureRelated, PicturesMixin, PublishableMixin, GeotrekMapEntityMixin
):
    topo_object = models.OneToOneField(
        Topology, parent_link=True, on_delete=models.CASCADE
    )
    departure = models.CharField(
        verbose_name=_("Departure"),
        max_length=128,
        blank=True,
        help_text=_("Departure description"),
    )
    arrival = models.CharField(
        verbose_name=_("Arrival"),
        max_length=128,
        blank=True,
        help_text=_("Arrival description"),
    )
    description_teaser = models.TextField(
        verbose_name=_("Description teaser"),
        blank=True,
        help_text=_("A brief summary (map pop-ups)"),
    )
    description = models.TextField(
        verbose_name=_("Description"), blank=True, help_text=_("Complete description")
    )
    ambiance = models.TextField(
        verbose_name=_("Ambiance"),
        blank=True,
        help_text=_("Main attraction and interest"),
    )
    access = models.TextField(
        verbose_name=_("Access"), blank=True, help_text=_("Best way to go")
    )
    duration = models.FloatField(
        verbose_name=_("Duration"),
        null=True,
        blank=True,
        help_text=_("In hours (1.5 = 1 h 30, 24 = 1 day, 48 = 2 days)"),
        validators=[MinValueValidator(0)],
    )
    advised_parking = models.CharField(
        verbose_name=_("Advised parking"),
        max_length=128,
        blank=True,
        help_text=_("Where to park"),
    )
    parking_location = models.PointField(
        verbose_name=_("Parking location"),
        srid=settings.SRID,
        spatial_index=False,
        blank=True,
        null=True,
    )
    public_transport = models.TextField(
        verbose_name=_("Public transport"),
        blank=True,
        help_text=_("Train, bus (see web links)"),
    )
    advice = models.TextField(
        verbose_name=_("Advice"),
        blank=True,
        help_text=_("Risks, danger, best period, ..."),
    )
    ratings = models.ManyToManyField(
        Rating, related_name="treks", blank=True, verbose_name=_("Ratings")
    )
    ratings_description = models.TextField(
        verbose_name=_("Ratings description"), blank=True
    )
    gear = models.TextField(
        verbose_name=_("Gear"), blank=True, help_text=_("Gear needed, adviced ...")
    )
    themes = models.ManyToManyField(
        Theme,
        related_name="treks",
        blank=True,
        verbose_name=_("Themes"),
        help_text=_("Main theme(s)"),
    )
    networks = models.ManyToManyField(
        "TrekNetwork",
        related_name="treks",
        blank=True,
        verbose_name=_("Networks"),
        help_text=_("Hiking networks"),
    )
    practice = models.ForeignKey(
        "Practice",
        related_name="treks",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Practice"),
    )
    accessibilities = models.ManyToManyField(
        "Accessibility",
        related_name="treks",
        blank=True,
        verbose_name=_("Accessibility type"),
    )
    accessibility_advice = models.TextField(
        verbose_name=_("Accessibility advice"),
        blank=True,
        help_text=_(
            "Specific elements allowing to appreciate the context "
            "of the itinerary for PRMs (advice, delicate passages, etc.)"
        ),
    )
    accessibility_covering = models.TextField(
        verbose_name=_("Accessibility covering"),
        blank=True,
        help_text=_(
            "Description of the surfaces encountered on the "
            "entire route. Track, path, road + type of "
            "surface (stony, presence of stones, sand, "
            "paving, slab...)"
        ),
    )
    accessibility_level = models.ForeignKey(
        "AccessibilityLevel",
        related_name="treks",
        blank=True,
        verbose_name=_("Level accessibility"),
        null=True,
        on_delete=models.PROTECT,
        help_text=_(
            "Beginner (Little drop – terrain without difficulties) / Experienced "
            "(Significant slope – Technical terrain, with obstacles)"
        ),
    )
    accessibility_exposure = models.TextField(
        verbose_name=_("Accessibility exposure"),
        blank=True,
        help_text=_(
            "Description of exposures and shaded areas. "
            "Shaded, High exposure, Presence of shaded areas"
        ),
    )
    accessibility_infrastructure = models.TextField(
        verbose_name=_("Accessibility infrastructure"),
        blank=True,
        help_text=_("Any specific accessibility infrastructure"),
    )
    accessibility_signage = models.TextField(
        verbose_name=_("Accessibility signage"),
        blank=True,
        help_text=_("Description of the size, shape and colors of signages."),
    )
    accessibility_slope = models.TextField(
        verbose_name=_("Accessibility slope"),
        blank=True,
        help_text=_(
            "Description of the slope: greater than 10% "
            "(Requires assistance when the slope is greater "
            "than 8%); slope break"
        ),
    )
    accessibility_width = models.TextField(
        verbose_name=_("Accessibility width"),
        blank=True,
        help_text=_(
            "Description of the narrowing of the trails and the "
            "minimum width for wheelchairs (Trail>0.90 m, "
            "Joëlette, Narrow trail requiring strong driving "
            "technique)"
        ),
    )
    route = models.ForeignKey(
        "Route",
        related_name="treks",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Route"),
    )
    difficulty = models.ForeignKey(
        "DifficultyLevel",
        related_name="treks",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("Difficulty"),
    )
    web_links = models.ManyToManyField(
        "WebLink",
        related_name="treks",
        blank=True,
        verbose_name=_("Web links"),
        help_text=_("External resources"),
    )
    information_desks = models.ManyToManyField(
        tourism_models.InformationDesk,
        related_name="treks",
        blank=True,
        verbose_name=_("Information desks"),
        help_text=_("Where to obtain information"),
    )
    points_reference = models.MultiPointField(
        verbose_name=_("Points of reference"),
        srid=settings.SRID,
        spatial_index=False,
        blank=True,
        null=True,
    )
    source = models.ManyToManyField(
        "common.RecordSource",
        blank=True,
        related_name="treks",
        verbose_name=_("Source"),
    )
    portal = models.ManyToManyField(
        "common.TargetPortal",
        blank=True,
        related_name="treks",
        verbose_name=_("Portal"),
    )
    labels = models.ManyToManyField(
        "common.Label", related_name="treks", verbose_name=_("Labels"), blank=True
    )
    eid = models.CharField(
        verbose_name=_("External id"), max_length=1024, blank=True, null=True
    )
    provider = models.CharField(
        verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True
    )
    eid2 = models.CharField(
        verbose_name=_("Second external id"), max_length=1024, blank=True, null=True
    )
    pois_excluded = models.ManyToManyField(
        "Poi",
        related_name="excluded_treks",
        verbose_name=_("Excluded POIs"),
        blank=True,
    )
    reservation_system = models.ForeignKey(
        ReservationSystem,
        verbose_name=_("Reservation system"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    reservation_id = models.CharField(
        verbose_name=_("Reservation ID"), max_length=1024, blank=True
    )
    attachments_accessibility = GenericRelation("common.AccessibilityAttachment")
    view_points = GenericRelation("common.HDViewPoint", related_query_name="trek")

    capture_map_image_waitfor = (
        ".poi_enum_loaded.services_loaded.info_desks_loaded.ref_points_loaded"
    )

    geometry_types_allowed = ["LINESTRING"]
    objects = TrekManager()

    class Meta:
        verbose_name = _("Trek")
        verbose_name_plural = _("Treks")
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_map_image_url(self):
        return reverse("trekking:trek_map_image", args=[str(self.pk), get_language()])

    def get_map_image_path(self, language=None):
        lang = language or get_language()
        return os.path.join(
            "maps", "%s-%s-%s.png" % (self._meta.model_name, self.pk, lang)
        )

    def get_map_image_extent(self, srid=settings.API_SRID):
        extent = list(super().get_map_image_extent(srid))
        if self.parking_location:
            self.parking_location.transform(srid)
            extent[0] = min(extent[0], self.parking_location.x)
            extent[1] = min(extent[1], self.parking_location.y)
            extent[2] = max(extent[2], self.parking_location.x)
            extent[3] = max(extent[3], self.parking_location.y)
        if self.points_reference:
            self.points_reference.transform(srid)
            prextent = self.points_reference.extent
            extent[0] = min(extent[0], prextent[0])
            extent[1] = min(extent[1], prextent[1])
            extent[2] = max(extent[2], prextent[2])
            extent[3] = max(extent[3], prextent[3])
        for poi in self.published_pois:
            poi.geom.transform(srid)
            extent[0] = min(extent[0], poi.geom.x)
            extent[1] = min(extent[1], poi.geom.y)
            extent[2] = max(extent[2], poi.geom.x)
            extent[3] = max(extent[3], poi.geom.y)
        return extent

    @property
    def poi_types(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Can't use values_list and must add 'ordering' because of bug:
            # https://code.djangoproject.com/ticket/14930
            values = self.pois.values("ordering", "type")
        else:
            values = self.pois.values("type")
        pks = [value["type"] for value in values]
        return POIType.objects.filter(pk__in=set(pks))

    @property
    def length_kilometer(self):
        return "%.1f" % (self.length_2d / 1000.0) if self.length_2d else None

    @property
    def networks_display(self):
        return ", ".join([str(n) for n in self.networks.all()])

    @property
    def districts_display(self):
        return ", ".join([str(d) for d in self.districts])

    @property
    def themes_display(self):
        return ", ".join([str(n) for n in self.themes.all()])

    @property
    def information_desks_display(self):
        return ", ".join([str(n) for n in self.information_desks.all()])

    @property
    def accessibilities_display(self):
        return ", ".join([str(n) for n in self.accessibilities.all()])

    @property
    def web_links_display(self):
        return ", ".join([str(n) for n in self.web_links.all()])

    @property
    def city_departure(self):
        cities = self.published_cities
        return str(cities[0]) if len(cities) > 0 else ""

    def kml(self):
        """Exports trek into KML format, add geometry as linestring and POI
        as place marks"""
        kml = simplekml.Kml()
        # Main itinerary
        geom3d = self.geom_3d.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newlinestring(
            name=self.name,
            description=plain_text(self.description),
            coords=simplify_coords(geom3d.coords),
        )
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        # Place marks
        for poi in self.published_pois:
            place = poi.geom_3d.transform(settings.API_SRID, clone=True)
            kml.newpoint(
                name=poi.name,
                description=plain_text(poi.description),
                coords=simplify_coords([place.coords]),
            )
        return kml.kml()

    def has_geom_valid(self):
        """A trek should be a LineString, even if it's a loop."""
        return super().has_geom_valid() and self.geom.geom_type.lower() == "linestring"

    @property
    def duration_pretty(self):
        return geotrek_tags.duration(self.duration)

    @classproperty
    def duration_pretty_verbose_name(cls):
        return _("Formated duration")

    @classmethod
    def path_treks(cls, path):
        treks = cls.objects.existing().filter(aggregations__path=path)
        # The following part prevents conflict with default trek ordering
        # ProgrammingError: SELECT DISTINCT ON expressions must match initial ORDER BY expressions
        return treks.order_by("topo_object").distinct("topo_object")

    @classmethod
    def topology_treks(cls, topology, queryset=None):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology, all_objects=queryset)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = queryset_or_all_objects(queryset, cls)
            qs = qs.filter(geom__intersects=area)

        # This prevents auto-intersection for treks
        if cls is topology.__class__:
            qs = qs.exclude(pk=topology.pk)

        return qs

    @classmethod
    def published_topology_treks(cls, topology):
        return cls.topology_treks(topology).filter(published=True)

    @classmethod
    def outdoor_treks(cls, outdoor_object, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=outdoor_object)

    @classmethod
    def tourism_treks(cls, tourism_object, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=tourism_object)

    @classmethod
    def get_create_label(cls):
        return _("Add a new trek")

    @property
    def parents(self):
        return Trek.objects.filter(trek_children__child=self, deleted=False)

    @property
    def parents_id(self):
        parents = self.trek_parents.values_list("parent__id", flat=True)
        return list(parents)

    @property
    def children(self):
        return Trek.objects.filter(trek_parents__parent=self, deleted=False).order_by(
            "trek_parents__order"
        )

    @property
    def children_id(self):
        """
        Get children IDs
        """
        children = self.trek_children.order_by("order").values_list(
            "child__id", flat=True
        )
        return children

    def previous_id_for(self, parent):
        children_id = list(parent.children_id)
        index = children_id.index(self.id)
        if index == 0:
            return None
        return children_id[index - 1]

    def next_id_for(self, parent):
        children_id = list(parent.children_id)
        index = children_id.index(self.id)
        if index == len(children_id) - 1:
            return None
        return children_id[index + 1]

    @property
    def previous_id(self):
        """
        Dict of parent -> previous child
        """
        return {
            parent.id: self.previous_id_for(parent)
            for parent in self.parents.filter(published=True, deleted=False)
        }

    @property
    def next_id(self):
        """
        Dict of parent -> next child
        """
        return {
            parent.id: self.next_id_for(parent)
            for parent in self.parents.filter(published=True, deleted=False)
        }

    def clean(self):
        """
        Custom model validation
        """
        if self.pk and self.pk in self.trek_children.values_list(
            "child__id", flat=True
        ):
            raise ValidationError(_("Cannot use itself as child trek."))

    def distance(self, to_cls):
        if self.practice and self.practice.distance is not None:
            return self.practice.distance
        else:
            return settings.TOURISM_INTERSECTION_MARGIN

    def is_public(self):
        for parent in self.parents:
            if parent.any_published:
                return True
        return self.any_published

    @property
    def picture_print(self):
        picture = super().picture_print
        if picture:
            return picture
        for poi in self.published_pois:
            picture = poi.picture_print
            if picture:
                return picture

    def save(self, *args, **kwargs):
        if self.pk is not None and kwargs.get("update_fields", None) is None:
            field_names = set()
            for field in self._meta.concrete_fields:
                if not field.primary_key and not hasattr(field, "through"):
                    field_names.add(field.attname)
            old_trek = Trek.objects.get(pk=self.pk)
            if self.geom is not None and old_trek.geom.equals_exact(
                self.geom, tolerance=0.00001
            ):
                field_names.remove("geom")
            if self.geom_3d is not None and old_trek.geom_3d.equals_exact(
                self.geom_3d, tolerance=0.00001
            ):
                field_names.remove("geom_3d")
            return super().save(update_fields=field_names, *args, **kwargs)
        super().save(*args, **kwargs)

    def duplicate(self, **kwargs):
        clone = super().duplicate(**kwargs)
        for attachment in AccessibilityAttachment.objects.filter(object_id=self.pk):
            clone_attachment(
                attachment,
                "attachment_file",
                {"content_object": clone, "uuid": get_uuid_duplication},
            )
        return clone

    @property
    def portal_display(self):
        return ", ".join([str(portal) for portal in self.portal.all()])

    @property
    def source_display(self):
        return ",".join([str(source) for source in self.source.all()])

    @property
    def published_labels(self):
        return [label for label in self.labels.all() if label.published]

    @property
    def extent(self):
        return (
            self.geom.transform(settings.API_SRID, clone=True).extent
            if self.geom.extent
            else None
        )

    def get_printcontext(self):
        maplayers = [
            settings.LEAFLET_CONFIG["TILES"][0][0],
        ]
        if settings.SHOW_SENSITIVE_AREAS_ON_MAP_SCREENSHOT:
            maplayers.append(gettext("Sensitive area"))
        if settings.SHOW_POIS_ON_MAP_SCREENSHOT:
            maplayers.append(gettext("POIs"))
        if settings.SHOW_SERVICES_ON_MAP_SCREENSHOT:
            maplayers.append(gettext("Services"))
        if settings.SHOW_SIGNAGES_ON_MAP_SCREENSHOT:
            maplayers.append(gettext("Signages"))
        if settings.SHOW_INFRASTRUCTURES_ON_MAP_SCREENSHOT:
            maplayers.append(gettext("Infrastructures"))
        return {"maplayers": maplayers}


@receiver(pre_delete, sender=Topology)
def log_cascade_deletion_from_trek_topology(sender, instance, using, **kwargs):
    # Treks are deleted when Topologies are deleted
    log_cascade_deletion(sender, instance, Trek, "topo_object")


Path.add_property("treks", Trek.path_treks, _("Treks"))
Topology.add_property("treks", Trek.topology_treks, _("Treks"))
if settings.HIDE_PUBLISHED_TREKS_IN_TOPOLOGIES:
    Topology.add_property("published_treks", lambda self: [], _("Published treks"))
else:
    Topology.add_property(
        "published_treks",
        lambda self: intersecting(Trek, self).filter(published=True),
        _("Published treks"),
    )
Intervention.add_property(
    "treks", lambda self: self.target.treks if self.target else [], _("Treks")
)
Project.add_property("treks", lambda self: self.edges_by_attr("treks"), _("Treks"))
tourism_models.TouristicContent.add_property("treks", Trek.tourism_treks, _("Treks"))
tourism_models.TouristicContent.add_property(
    "published_treks",
    lambda self: intersecting(Trek, self).filter(published=True),
    _("Published treks"),
)
tourism_models.TouristicEvent.add_property("treks", Trek.tourism_treks, _("Treks"))
tourism_models.TouristicEvent.add_property(
    "published_treks",
    lambda self: intersecting(Trek, self).filter(published=True),
    _("Published treks"),
)
if "geotrek.signage" in settings.INSTALLED_APPS:
    Blade.add_property("treks", lambda self: self.signage.treks, _("Treks"))
    Blade.add_property(
        "published_treks",
        lambda self: self.signage.published_treks,
        _("Published treks"),
    )


class TrekNetwork(TimeStampedModelMixin, PictogramMixin):
    network = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Trek network")
        verbose_name_plural = _("Trek networks")
        ordering = ["network"]

    def __str__(self):
        return self.network


class Accessibility(TimeStampedModelMixin, OptionalPictogramMixin):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    cirkwi = models.ForeignKey(
        "cirkwi.CirkwiTag",
        verbose_name=_("Cirkwi tag"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    id_prefix = "A"

    class Meta:
        verbose_name = _("Accessibility")
        verbose_name_plural = _("Accessibilities")
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def slug(self):
        return slugify(self.name) or str(self.pk)


class AccessibilityLevel(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Accessibility level")
        verbose_name_plural = _("Accessibility levels")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Route(TimeStampedModelMixin, OptionalPictogramMixin):
    route = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Route")
        verbose_name_plural = _("Routes")
        ordering = ["route"]

    def __str__(self):
        return self.route


class DifficultyLevel(TimeStampedModelMixin, OptionalPictogramMixin):
    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order difficulty levels, especially in public website
    where treks are filtered by difficulty ids.
    """

    id = models.IntegerField(primary_key=True)
    difficulty = models.CharField(verbose_name=_("Difficulty level"), max_length=128)
    cirkwi_level = models.IntegerField(
        verbose_name=_("Cirkwi level"),
        blank=True,
        null=True,
        help_text=_("Between 1 and 8"),
    )
    cirkwi = models.ForeignKey(
        "cirkwi.CirkwiTag",
        verbose_name=_("Cirkwi tag"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("Difficulty level")
        verbose_name_plural = _("Difficulty levels")
        ordering = ["id"]

    def __str__(self):
        return self.difficulty

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by("-id")[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super().save(*args, **kwargs)


class WebLink(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    url = models.URLField(verbose_name=_("URL"), max_length=2048)
    category = models.ForeignKey(
        "WebLinkCategory",
        verbose_name=_("Category"),
        related_name="links",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = WebLinkManager()

    class Meta:
        verbose_name = _("Web link")
        verbose_name_plural = _("Web links")
        ordering = ["name"]

    def __str__(self):
        category = "%s - " % self.category.label if self.category else ""
        return "%s%s" % (category, self.name)

    @classmethod
    def get_add_url(cls):
        return reverse("trekking:weblink_add")


class WebLinkCategory(TimeStampedModelMixin, PictogramMixin):
    label = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Web link category")
        verbose_name_plural = _("Web link categories")
        ordering = ["label"]

    def __str__(self):
        return "%s" % self.label


class POI(
    StructureRelated, PicturesMixin, PublishableMixin, GeotrekMapEntityMixin, Topology
):
    topo_object = models.OneToOneField(
        Topology, parent_link=True, on_delete=models.CASCADE
    )
    description = models.TextField(
        verbose_name=_("Description"), blank=True, help_text=_("History, details,  ...")
    )
    type = models.ForeignKey(
        "POIType", related_name="pois", verbose_name=_("Type"), on_delete=models.PROTECT
    )
    eid = models.CharField(
        verbose_name=_("External id"), max_length=1024, blank=True, null=True
    )
    provider = models.CharField(
        verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True
    )
    view_points = GenericRelation("common.HDViewPoint", related_query_name="poi")

    geometry_types_allowed = ["POINT"]

    class Meta:
        verbose_name = _("POI")
        verbose_name_plural = _("POI")

    # Override default manager
    objects = POIManager()

    # Do no check structure when selecting POIs to exclude
    check_structure_in_forms = False

    def __str__(self):
        return "%s (%s)" % (self.name, self.type)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Invalidate treks map
        for trek in self.treks.all():
            try:
                os.remove(trek.get_map_image_path())
            except OSError:
                pass

    @property
    def type_display(self):
        return str(self.type)

    @classmethod
    def path_pois(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct("pk")

    @classmethod
    def topology_pois(cls, topology, queryset=None):
        return cls.exclude_pois(cls.topology_all_pois(topology, queryset), topology)

    @classmethod
    def topology_all_pois(cls, topology, queryset=None):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology, all_objects=queryset)
        else:
            object_geom = topology.geom.transform(settings.SRID, clone=True).buffer(
                settings.TREK_POI_INTERSECTION_MARGIN
            )
            qs = queryset_or_all_objects(queryset, cls)
            qs = qs.filter(geom__intersects=object_geom)
            if topology.geom.geom_type == "LineString":
                qs = qs.annotate(
                    locate=LineLocatePoint(
                        Transform(topology.geom, settings.SRID),
                        Transform(F("geom"), settings.SRID),
                    )
                )
                qs = qs.order_by("locate")

        return qs.select_related("type")

    @classmethod
    def outdoor_all_pois(cls, obj):
        object_geom = obj.geom.transform(settings.SRID, clone=True).buffer(
            settings.OUTDOOR_INTERSECTION_MARGIN
        )
        qs = cls.objects.existing().filter(geom__intersects=object_geom)
        qs = qs.order_by("pk")
        return qs

    @classmethod
    def tourism_pois(cls, tourism_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=tourism_obj)

    @classmethod
    def published_topology_pois(cls, topology):
        return cls.topology_pois(topology).filter(published=True)

    def distance(self, to_cls):
        return settings.TOURISM_INTERSECTION_MARGIN

    @classmethod
    def exclude_pois(cls, qs, topology):
        try:
            return qs.exclude(
                pk__in=topology.trek.pois_excluded.values_list("pk", flat=True)
            )
        except Trek.DoesNotExist:
            return qs

    @property
    def extent(self):
        return (
            self.geom.transform(settings.API_SRID, clone=True).extent
            if self.geom
            else None
        )


@receiver(pre_delete, sender=Topology)
def log_cascade_deletion_from_poi_topology(sender, instance, using, **kwargs):
    # POIs are deleted when Topologies are deleted
    log_cascade_deletion(sender, instance, POI, "topo_object")


Path.add_property("pois", POI.path_pois, _("POIs"))
Topology.add_property("pois", POI.topology_pois, _("POIs"))
Topology.add_property("all_pois", POI.topology_all_pois, _("POIs"))
Topology.add_property(
    "published_pois", POI.published_topology_pois, _("Published POIs")
)
Intervention.add_property(
    "pois", lambda self: self.target.pois if self.target else [], _("POIs")
)
Project.add_property("pois", lambda self: self.edges_by_attr("pois"), _("POIs"))
tourism_models.TouristicContent.add_property("pois", POI.tourism_pois, _("POIs"))
tourism_models.TouristicContent.add_property(
    "published_pois",
    lambda self: intersecting(POI, self).filter(published=True),
    _("Published POIs"),
)
tourism_models.TouristicEvent.add_property("pois", POI.tourism_pois, _("POIs"))
tourism_models.TouristicEvent.add_property(
    "published_pois",
    lambda self: intersecting(POI, self).filter(published=True),
    _("Published POIs"),
)
if "geotrek.signage" in settings.INSTALLED_APPS:
    Blade.add_property("pois", lambda self: self.signage.pois, _("POIs"))
    Blade.add_property(
        "published_pois", lambda self: self.signage.published_pois, _("Published POIs")
    )


class POIType(TimeStampedModelMixin, PictogramMixin):
    label = models.CharField(verbose_name=_("Name"), max_length=128)
    cirkwi = models.ForeignKey(
        "cirkwi.CirkwiPOICategory",
        verbose_name=_("Cirkwi POI category"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _("POI type")
        verbose_name_plural = _("POI types")
        ordering = ["label"]

    def __str__(self):
        return self.label


class ServiceType(TimeStampedModelMixin, PictogramMixin, BasePublishableMixin):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=128,
        help_text=_("Public name (Change carefully)"),
    )
    practices = models.ManyToManyField(
        "Practice", related_name="services", blank=True, verbose_name=_("Practices")
    )

    class Meta:
        verbose_name = _("Service type")
        verbose_name_plural = _("Service types")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(StructureRelated, GeotrekMapEntityMixin, Topology):
    topo_object = models.OneToOneField(
        Topology, parent_link=True, on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        "ServiceType",
        related_name="services",
        verbose_name=_("Type"),
        on_delete=models.PROTECT,
    )
    eid = models.CharField(
        verbose_name=_("External id"), max_length=1024, blank=True, null=True
    )
    provider = models.CharField(
        verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True
    )

    objects = ServiceManager()

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self):
        return str(self.type)

    @property
    def name(self):
        return self.type.name

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s">%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.name,
            self.name,
        )
        if self.type.published:
            s = (
                '<span class="badge badge-success" title="%s">&#x2606;</span> '
                % _("Published")
                + s
            )
        return s

    @classproperty
    def name_verbose_name(cls):
        return _("Type")

    @property
    def type_display(self):
        return str(self.type)

    @classmethod
    def path_services(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct("pk")

    @classmethod
    def topology_services(cls, topology, queryset=None):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology, all_objects=queryset)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = queryset_or_all_objects(queryset, cls)
            qs = qs.filter(geom__intersects=area)
        if isinstance(topology, Trek):
            qs = qs.filter(type__practices=topology.practice)
        return qs

    @classmethod
    def published_topology_services(cls, topology):
        return cls.topology_services(topology).filter(type__published=True)

    def distance(self, to_cls):
        return settings.TOURISM_INTERSECTION_MARGIN

    @classmethod
    def outdoor_services(cls, outdoor_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=outdoor_obj)

    @classmethod
    def tourism_services(cls, tourism_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=tourism_obj)


@receiver(pre_delete, sender=Topology)
def log_cascade_deletion_from_service_topology(sender, instance, using, **kwargs):
    # Services are deleted when Topologies are deleted
    log_cascade_deletion(sender, instance, Service, "topo_object")


Path.add_property("services", Service.path_services, _("Services"))
Topology.add_property("services", Service.topology_services, _("Services"))
Topology.add_property(
    "published_services", Service.published_topology_services, _("Published Services")
)
Intervention.add_property(
    "services", lambda self: self.target.services if self.target else [], _("Services")
)
Project.add_property(
    "services", lambda self: self.edges_by_attr("services"), _("Services")
)
tourism_models.TouristicContent.add_property(
    "services", Service.tourism_services, _("Services")
)
tourism_models.TouristicContent.add_property(
    "published_services",
    lambda self: intersecting(Service, self).filter(published=True),
    _("Published Services"),
)
tourism_models.TouristicEvent.add_property(
    "services", Service.tourism_services, _("Services")
)
tourism_models.TouristicEvent.add_property(
    "published_services",
    lambda self: intersecting(Service, self).filter(published=True),
    _("Published Services"),
)
if "geotrek.signage" in settings.INSTALLED_APPS:
    Blade.add_property("services", lambda self: self.signage.services, _("Services"))
    Blade.add_property(
        "published_services",
        lambda self: self.signage.published_pois,
        _("Published Services"),
    )
