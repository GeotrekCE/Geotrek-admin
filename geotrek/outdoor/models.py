import uuid
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.postgres.indexes import GistIndex
from django.core.validators import MinValueValidator
from django.db.models import Q
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from geotrek.altimetry.models import AltimetryMixin as BaseAltimetryMixin
from geotrek.authent.models import StructureRelated
from geotrek.common.mixins.models import (AddPropertyMixin, OptionalPictogramMixin, PicturesMixin, PublishableMixin, TimeStampedModelMixin, GeotrekMapEntityMixin)
from geotrek.common.models import Organism, RatingMixin, RatingScaleMixin
from geotrek.common.templatetags import geotrek_tags
from geotrek.common.utils import intersecting
from geotrek.core.models import Path, Topology, Trail
from geotrek.infrastructure.models import Infrastructure
from geotrek.maintenance.models import Intervention
from geotrek.outdoor.managers import SiteManager, CourseOrderedChildManager, CourseManager
from geotrek.outdoor.mixins import ExcludedPOIsMixin
from geotrek.signage.models import Blade, Signage
from geotrek.tourism.models import TouristicContent, TouristicEvent
from geotrek.trekking.models import POI, Service, Trek
from geotrek.zoning.mixins import ZoningPropertiesMixin


class AltimetryMixin(BaseAltimetryMixin):
    def ispoint(self):
        return self.geom.num_geom == 1 and self.geom[0].geom_type == 'Point'

    class Meta:
        abstract = True


class Sector(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)

    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")
        ordering = ('name', )

    def __str__(self):
        return self.name


class Practice(TimeStampedModelMixin, OptionalPictogramMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    sector = models.ForeignKey(Sector, related_name="practices", on_delete=models.PROTECT,
                               verbose_name=_("Sector"), null=True, blank=True)

    class Meta:
        verbose_name = _("Practice")
        verbose_name_plural = _("Practices")
        ordering = ('name', )

    def __str__(self):
        return self.name


class RatingScale(RatingScaleMixin):
    practice = models.ForeignKey(Practice, related_name="rating_scales", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"))

    class Meta:
        verbose_name = _("Rating scale")
        verbose_name_plural = _("Rating scales")
        ordering = ('practice', 'order', 'name')


class Rating(RatingMixin):
    scale = models.ForeignKey(RatingScale, related_name="ratings", on_delete=models.PROTECT,
                              verbose_name=_("Scale"))

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")
        ordering = ('order', 'name')


class SiteType(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    practice = models.ForeignKey('Practice', related_name="site_types", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"), null=True, blank=True)

    class Meta:
        verbose_name = _("Site type")
        verbose_name_plural = _("Site types")
        ordering = ('name', )

    def __str__(self):
        return self.name


class CourseType(TimeStampedModelMixin, models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    practice = models.ForeignKey('Practice', related_name="course_types", on_delete=models.PROTECT,
                                 verbose_name=_("Practice"), null=True, blank=True)

    class Meta:
        verbose_name = _("Course type")
        verbose_name_plural = _("Course types")
        ordering = ('name', )

    def __str__(self):
        return self.name


class Site(ZoningPropertiesMixin, AddPropertyMixin, PicturesMixin, PublishableMixin, GeotrekMapEntityMixin,
           StructureRelated, AltimetryMixin, TimeStampedModelMixin, MPTTModel, ExcludedPOIsMixin):
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
    WIND_CHOICES = (
        ('N', _("↓ N")),
        ('NE', _("↙ NE")),
        ('E', _("← E")),
        ('SE', _("↖ SE")),
        ('S', _("↑ S")),
        ('SW', _("↗ SW")),
        ('W', _("→ W")),
        ('NW', _("↘ NW")),
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
    ratings = models.ManyToManyField(Rating, related_name='sites', blank=True, verbose_name=_("Ratings"))
    period = models.CharField(verbose_name=_("Period"), max_length=1024, blank=True)
    orientation = models.JSONField(verbose_name=_("Orientation"), default=list, blank=True)
    wind = models.JSONField(verbose_name=_("Wind"), default=list, blank=True)
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
    pois_excluded = models.ManyToManyField('trekking.Poi', related_name='excluded_sites', verbose_name=_("Excluded POIs"),
                                           blank=True)
    web_links = models.ManyToManyField('trekking.WebLink', related_name="sites", blank=True, verbose_name=_("Web links"),
                                       help_text=_("External resources"))
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)
    type = models.ForeignKey(SiteType, related_name="sites", on_delete=models.PROTECT,
                             verbose_name=_("Type"), null=True, blank=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    provider = models.CharField(verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True)
    managers = models.ManyToManyField(Organism, verbose_name=_("Managers"), blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    view_points = GenericRelation('common.HDViewPoint', related_query_name='site')

    check_structure_in_forms = False

    objects = SiteManager()

    class Meta:
        verbose_name = _("Outdoor site")
        verbose_name_plural = _("Outdoor sites")
        ordering = ('name', )
        indexes = [
            GistIndex(name='site_geom_3d_gist_idx', fields=['geom_3d']),
        ]

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    @property
    def name_display(self):
        return "- " * self.level + super().name_display

    def distance(self, to_cls):
        """Distance to associate this site to another class"""
        return settings.OUTDOOR_INTERSECTION_MARGIN

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
    def super_practices_id(self):
        """ Return practices of itself and its descendants as ids """
        practices_id = self.get_descendants(include_self=True) \
            .exclude(practice=None) \
            .values_list('practice_id', flat=True)
        return set(practices_id)

    @property
    def super_practices(self):
        """ Return practices of itself and its descendants as objects """
        return Practice.objects.filter(id__in=self.super_practices_id)  # Sorted and unique

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
    def super_ratings_id(self):
        """ Return ratings of itself and its descendants as ids """
        ratings_id = self.get_descendants(include_self=True) \
            .exclude(ratings=None) \
            .values_list('ratings', flat=True)
        return set(ratings_id)

    @property
    def super_ratings(self):
        """ Return ratings of itself and its descendants as objects """
        return Rating.objects.filter(id__in=self.super_ratings_id)  # Sorted and unique

    @property
    def super_sectors(self):
        """ Return sectors of itself and its descendants """
        sectors_id = self.get_descendants(include_self=True) \
            .exclude(practice=None) \
            .values_list('practice__sector_id', flat=True)
        return Sector.objects.filter(id__in=sectors_id)  # Sorted and unique

    @property
    def super_orientation(self):
        """ Return orientation of itself and its descendants """
        orientation = set(sum(self.get_descendants(include_self=True).values_list('orientation', flat=True), []))
        return [o for o, _o in self.ORIENTATION_CHOICES if o in orientation]  # Sorting

    @property
    def super_wind(self):
        """ Return wind of itself and its descendants """
        wind = set(sum(self.get_descendants(include_self=True).values_list('wind', flat=True), []))
        return [o for o, _o in self.WIND_CHOICES if o in wind]  # Sorting

    @property
    def super_managers(self):
        """ Return managers of itself and its descendants """
        sites = self.get_descendants(include_self=True)
        return Organism.objects.filter(site__in=sites)  # Sorted and unique

    @property
    def all_pois(self):
        return POI.outdoor_all_pois(self)

    def site_interventions(self):
        # Interventions on sites
        site_content_type = ContentType.objects.get_for_model(Site)
        qs = Q(target_type=site_content_type, target_id=self.id)
        # Interventions on topologies
        topologies = Topology.objects.existing() \
            .filter(geom__dwithin=(self.geom, D(m=settings.OUTDOOR_INTERSECTION_MARGIN))) \
            .values_list('pk', flat=True)
        not_topology_content_types = [
            site_content_type,
            ContentType.objects.get_for_model(Course),
            ContentType.objects.get_for_model(Blade),
        ]
        qs |= Q(target_id__in=topologies) & ~Q(target_type__in=not_topology_content_types)
        return Intervention.objects.existing().filter(qs).distinct('pk')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.refresh_from_db()


Path.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Topology.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
TouristicContent.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
TouristicEvent.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Blade.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Intervention.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))

Site.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Site.add_property('courses', lambda self: intersecting(Course, self), _("Parcours"))
Site.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Site.add_property('services', lambda self: intersecting(Service, self), _("Services"))
Site.add_property('trails', lambda self: intersecting(Trail, self), _("Trails"))
Site.add_property('infrastructures', lambda self: intersecting(Infrastructure, self), _("Infrastructures"))
Site.add_property('signages', lambda self: intersecting(Signage, self), _("Signages"))
Site.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _("Touristic contents"))
Site.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
Site.add_property('interventions', lambda self: Site.site_interventions(self), _("Interventions"))


class OrderedCourseChild(models.Model):
    parent = models.ForeignKey('Course', related_name='course_children', on_delete=models.CASCADE)
    child = models.ForeignKey('Course', related_name='course_parents', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=True, null=True)

    objects = CourseOrderedChildManager()

    class Meta:
        ordering = ('parent__id', 'order')
        unique_together = (
            ('parent', 'child'),
        )


class Course(ZoningPropertiesMixin, AddPropertyMixin, PublishableMixin, GeotrekMapEntityMixin,
             StructureRelated, PicturesMixin, AltimetryMixin, TimeStampedModelMixin, ExcludedPOIsMixin):
    geom = models.GeometryCollectionField(verbose_name=_("Location"), srid=settings.SRID)
    parent_sites = models.ManyToManyField(Site, related_name="children_courses", verbose_name=_("Sites"))
    description = models.TextField(verbose_name=_("Description"), blank=True,
                                   help_text=_("Complete description"))
    ratings_description = models.TextField(verbose_name=_("Ratings description"), blank=True)
    gear = models.TextField(verbose_name=_("Gear"), blank=True)
    duration = models.FloatField(verbose_name=_("Duration"), null=True, blank=True,
                                 help_text=_("In hours (1.5 = 1 h 30, 24 = 1 day, 48 = 2 days)"),
                                 validators=[MinValueValidator(0)])
    advice = models.TextField(verbose_name=_("Advice"), blank=True,
                              help_text=_("Risks, danger, best period, ..."))
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)
    equipment = models.TextField(verbose_name=_("Equipment"), blank=True)
    ratings = models.ManyToManyField(Rating, related_name='courses', blank=True, verbose_name=_("Ratings"))
    height = models.IntegerField(verbose_name=_("Height"), blank=True, null=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    provider = models.CharField(verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True)
    type = models.ForeignKey(CourseType, related_name="courses", on_delete=models.PROTECT,
                             verbose_name=_("Type"), null=True, blank=True)
    pois_excluded = models.ManyToManyField('trekking.Poi', related_name='excluded_courses', verbose_name=_("Excluded POIs"),
                                           blank=True)
    points_reference = models.MultiPointField(verbose_name=_("Points of reference"),
                                              srid=settings.SRID, spatial_index=False, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    check_structure_in_forms = False

    objects = CourseManager()

    class Meta:
        verbose_name = _("Outdoor course")
        verbose_name_plural = _("Outdoor courses")
        ordering = ('name', )
        indexes = [
            GistIndex(name='course_points_ref_gist_idx', fields=['points_reference']),
            GistIndex(name='course_geom_3d_gist_idx', fields=['geom_3d']),
        ]

    def __str__(self):
        return self.name

    def distance(self, to_cls):
        """Distance to associate this course to another class"""
        return settings.OUTDOOR_INTERSECTION_MARGIN

    @classmethod
    def get_create_label(cls):
        return _("Add a new outdoor course")

    @property
    def duration_pretty(self):
        return geotrek_tags.duration(self.duration)

    @property
    def parents(self):
        return Course.objects.filter(course_children__child=self)

    def parents_id(self):
        parents = self.course_parents.values_list('parent__id', flat=True)
        return parents

    @property
    def children(self):
        return Course.objects.filter(course_parents__parent=self).order_by('course_parents__order')

    @property
    def children_id(self):
        children = self.course_children.values_list('child__id', flat=True)
        return children

    @property
    def all_pois(self):
        return POI.outdoor_all_pois(self)

    @property
    def all_hierarchy_roots(self):
        """ Since a course has multiple parent sites, it belongs in multiple hierarchy trees.
            This method returns all hierarchy roots the course is a descendant of.
        """
        roots = []
        for site in self.parent_sites.all():
            roots.append(site.get_root())
        return list(set(roots))

    def course_interventions(self):
        # Interventions on courses
        course_content_type = ContentType.objects.get_for_model(Course)
        qs = Q(target_type=course_content_type, target_id=self.id)
        # Interventions on topologies
        topologies = Topology.objects.existing() \
            .filter(geom__dwithin=(self.geom, D(m=settings.OUTDOOR_INTERSECTION_MARGIN))) \
            .values_list('pk', flat=True)
        not_topology_content_types = [
            ContentType.objects.get_for_model(Site),
            course_content_type,
            ContentType.objects.get_for_model(Blade),
        ]
        qs |= Q(target_id__in=topologies) & ~Q(target_type__in=not_topology_content_types)
        return Intervention.objects.existing().filter(qs).distinct('pk')

    @property
    def parent_sites_display(self):
        return ", ".join(list(self.parent_sites.values_list("name", flat=True)))

    @property
    def points_reference_geojson(self):
        if self.points_reference:
            geojson = self.points_reference.transform(settings.API_SRID, clone=True).geojson
            return geojson
        return None


Path.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
Topology.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
TouristicContent.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
TouristicEvent.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
Blade.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))
Intervention.add_property('courses', lambda self: intersecting(Course, self), _("Courses"))

Course.add_property('sites', lambda self: intersecting(Site, self), _("Sites"))
Course.add_property('courses', lambda self: intersecting(Course, self), _("Parcours"))
Course.add_property('treks', lambda self: intersecting(Trek, self), _("Treks"))
Course.add_property('services', lambda self: intersecting(Service, self), _("Services"))
Course.add_property('trails', lambda self: intersecting(Trail, self), _("Trails"))
Course.add_property('infrastructures', lambda self: intersecting(Infrastructure, self), _("Infrastructures"))
Course.add_property('signages', lambda self: intersecting(Signage, self), _("Signages"))
Course.add_property('touristic_contents', lambda self: intersecting(TouristicContent, self), _("Touristic contents"))
Course.add_property('touristic_events', lambda self: intersecting(TouristicEvent, self), _("Touristic events"))
Course.add_property('interventions', lambda self: Course.course_interventions(self), _("Interventions"))
