from colorfield.fields import ColorField
from multiselectfield import MultiSelectField
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import Q
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from geotrek.altimetry.models import AltimetryMixin as BaseAltimetryMixin
from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import TimeStampedModelMixin, AddPropertyMixin, PublishableMixin, OptionalPictogramMixin
from geotrek.common.utils import intersecting
from geotrek.core.models import Path, Topology, Trail
from geotrek.infrastructure.models import Infrastructure
from geotrek.signage.models import Signage
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.trekking.models import Trek, POI
from geotrek.zoning.mixins import ZoningPropertiesMixin
from mapentity.models import MapEntityMixin
from mptt.models import MPTTModel, TreeForeignKey


class AltimetryMixin(BaseAltimetryMixin):
    def ispoint(self):
        return self.geom.num_geom == 1 and self.geom[0].geom_type == 'Point'

    class Meta:
        abstract = True


class Sector(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")
        ordering = ('name', )

    def __str__(self):
        return self.name


class Practice(OptionalPictogramMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    sector = models.ForeignKey(Sector, related_name="practices", on_delete=models.PROTECT,
                               verbose_name=_("Sector"), null=True, blank=True)

    class Meta:
        verbose_name = _("Practice")
        verbose_name_plural = _("Practices")
        ordering = ('name', )

    def __str__(self):
        return self.name


class RatingScale(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    practice = models.ForeignKey(Practice, related_name="rating_scales", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"))
    order = models.IntegerField(verbose_name=_("Order"), null=True, blank=True,
                                help_text=_("Within a practice. Alphabetical order if blank"))

    def __str__(self):
        return "{} ({})".format(self.name, self.practice.name)

    class Meta:
        verbose_name = _("Rating scale")
        verbose_name_plural = _("Rating scales")
        ordering = ('practice', 'order', 'name')


class Rating(OptionalPictogramMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    scale = models.ForeignKey(RatingScale, related_name="ratings", on_delete=models.PROTECT,
                              verbose_name=_("Scale"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    order = models.IntegerField(verbose_name=_("Order"), null=True, blank=True,
                                help_text=_("Alphabetical order if blank"))
    color = ColorField(verbose_name=_("Color"), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")
        ordering = ('order', 'name')


class SiteType(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    practice = models.ForeignKey('Practice', related_name="types", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"), null=True, blank=True)

    class Meta:
        verbose_name = _("Site type")
        verbose_name_plural = _("Site types")
        ordering = ('name', )

    def __str__(self):
        return self.name


class Site(ZoningPropertiesMixin, AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
           AltimetryMixin, TimeStampedModelMixin, MPTTModel):
    ORIENTATION_CHOICES = (
        ('N', _("↑ N")),
        ('NE', _("↗ NE")),
        ('E', _("→ E")),
        ('SE', _("↘ SE")),
        ('S', _("↓ S")),
        ('SW', _("↙ SW")),
        ('W', _("← W")),
        ('NW', _("↖ NW")),
    )

    geom = models.GeometryCollectionField(verbose_name=_("Location"), srid=settings.SRID)
    parent = TreeForeignKey('Site', related_name="children", on_delete=models.PROTECT,
                            verbose_name=_("Parent"), null=True, blank=True)
    practice = models.ForeignKey('Practice', related_name="sites", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Complete description"))
    description_teaser = models.TextField(verbose_name=_("Description teaser"), blank=True,
                                          help_text=_("A brief summary (map pop-ups)"))
    ambiance = models.TextField(verbose_name=_("Ambiance"), blank=True,
                                help_text=_("Main attraction and interest"))
    advice = models.TextField(verbose_name=_("Advice"), blank=True,
                              help_text=_("Risks, danger, best period, ..."))
    ratings_min = models.ManyToManyField(Rating, related_name='sites_min', blank=True)
    ratings_max = models.ManyToManyField(Rating, related_name='sites_max', blank=True)
    period = models.CharField(verbose_name=_("Period"), max_length=1024, blank=True)
    orientation = MultiSelectField(verbose_name=_("Orientation"), blank=True, max_length=20, choices=ORIENTATION_CHOICES)
    wind = MultiSelectField(verbose_name=_("Wind"), blank=True, max_length=20, choices=ORIENTATION_CHOICES)
    labels = models.ManyToManyField('common.Label', related_name='sites', blank=True,
                                    verbose_name=_("Labels"))
    themes = models.ManyToManyField('common.Theme', related_name="sites", blank=True, verbose_name=_("Themes"),
                                    help_text=_("Main theme(s)"))
    information_desks = models.ManyToManyField('tourism.InformationDesk', related_name='sites',
                                               blank=True, verbose_name=_("Information desks"),
                                               help_text=_("Where to obtain information"))
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='sites',
                                    verbose_name=_("Portal"))
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='sites',
                                    verbose_name=_("Source"))
    web_links = models.ManyToManyField('trekking.WebLink', related_name="sites", blank=True, verbose_name=_("Web links"),
                                       help_text=_("External resources"))
    type = models.ForeignKey(SiteType, related_name="sites", on_delete=models.PROTECT,
                             verbose_name=_("Type"), null=True, blank=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = _("Outdoor site")
        verbose_name_plural = _("Outdoor sites")
        ordering = ('name', )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    @property
    def name_display(self):
        return "- " * self.level + super().name_display

    def distance(self, to_cls):
        """Distance to associate this site to another class"""
        return None

    @classmethod
    def get_create_label(cls):
        return _("Add a new outdoor site")

    @property
    def published_children(self):
        if not settings.PUBLISHED_BY_LANG:
            return self.children.filter(published=True)
        q = Q()
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            q |= Q(**{'published_{}'.format(lang): True})
        return self.children.filter(q)

    @property
    def super_practices(self):
        "Return practices of itself and its descendants"
        practices_id = self.get_descendants(include_self=True) \
            .exclude(practice=None) \
            .values_list('practice_id', flat=True)
        return Practice.objects.filter(id__in=practices_id)  # Sorted and unique

    @property
    def super_practices_display(self):
        practices = self.super_practices
        if not practices:
            return ""
        verbose = [
            str(practice) if practice == self.practice else "<i>{}</i>".format(escape(practice))
            for practice in practices
        ]
        return ", ".join(verbose)
    super_practices_verbose_name = _('Practices')

    @property
    def super_sectors(self):
        "Return sectors of itself and its descendants"
        sectors_id = self.get_descendants(include_self=True) \
            .exclude(practice=None) \
            .values_list('practice__sector_id', flat=True)
        return Sector.objects.filter(id__in=sectors_id)  # Sorted and unique

    @property
    def super_orientation(self):
        "Return orientation of itself and its descendants"
        orientation = set(sum(self.get_descendants(include_self=True).values_list('orientation', flat=True), []))
        return [o for o, _o in self.ORIENTATION_CHOICES if o in orientation]  # Sorting

    @property
    def super_wind(self):
        "Return wind of itself and its descendants"
        wind = set(sum(self.get_descendants(include_self=True).values_list('wind', flat=True), []))
        return [o for o, _o in self.ORIENTATION_CHOICES if o in wind]  # Sorting


Path.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Topology.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
TouristicContent.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
TouristicEvent.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))

Site.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Site.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Site.add_property('pois', lambda self: intersecting(POI, self), _("POIs"))
Site.add_property('trails', lambda self: intersecting(Trail, self), _("Trails"))
Site.add_property('infrastructures', lambda self: intersecting(Infrastructure, self), _("Infrastructures"))
Site.add_property('signages', lambda self: intersecting(Signage, self), _("Signages"))
Site.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _("Touristic contents"))
Site.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))


class Course(ZoningPropertiesMixin, AddPropertyMixin, PublishableMixin, MapEntityMixin, StructureRelated,
             AltimetryMixin, TimeStampedModelMixin):
    geom = models.GeometryCollectionField(verbose_name=_("Location"), srid=settings.SRID)
    site = models.ForeignKey(Site, related_name="courses", on_delete=models.PROTECT, verbose_name=_("Site"))
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Complete description"))
    advice = models.TextField(verbose_name=_("Advice"), blank=True,
                              help_text=_("Risks, danger, best period, ..."))
    equipment = models.TextField(verbose_name=_("Equipment"), blank=True)
    ratings = models.ManyToManyField(Rating, related_name='courses', blank=True)
    height = models.IntegerField(verbose_name=_("Height"), blank=True, null=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = _("Outdoor course")
        verbose_name_plural = _("Outdoor courses")
        ordering = ('name', )

    def __str__(self):
        return self.name

    def distance(self, to_cls):
        """Distance to associate this site to another class"""
        return None

    @classmethod
    def get_create_label(cls):
        return _("Add a new outdoor course")


Path.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
Topology.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
TouristicContent.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
TouristicEvent.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))

Course.add_property('sites', lambda self: intersecting(Course, self), _("Sites"))
Course.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Course.add_property('pois', lambda self: intersecting(POI, self), _("POIs"))
Course.add_property('trails', lambda self: intersecting(Trail, self), _("Trails"))
Course.add_property('infrastructures', lambda self: intersecting(Infrastructure, self), _("Infrastructures"))
Course.add_property('signages', lambda self: intersecting(Signage, self), _("Signages"))
Course.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _("Touristic contents"))
Course.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
