import os
import logging

from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

import simplekml
from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text

from geotrek.authent.models import StructureRelated
from geotrek.core.models import Path, Topology
from geotrek.common.utils import intersecting, classproperty
from geotrek.common.mixins import (PicturesMixin, PublishableMixin,
                                   PictogramMixin, OptionalPictogramMixin)
from geotrek.common.models import Theme
from geotrek.maintenance.models import Intervention, Project
from geotrek.tourism import models as tourism_models

from .templatetags import trekking_tags


logger = logging.getLogger(__name__)


class Trek(StructureRelated, PicturesMixin, PublishableMixin, MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=128, blank=True,
                                 help_text=_(u"Departure description"), db_column='depart')
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=128, blank=True,
                               help_text=_(u"Arrival description"), db_column='arrivee')

    description_teaser = models.TextField(verbose_name=_(u"Description teaser"), blank=True,
                                          help_text=_(u"A brief summary (map pop-ups)"), db_column='chapeau')
    description = models.TextField(verbose_name=_(u"Description"), blank=True, db_column='description',
                                   help_text=_(u"Complete description"))
    ambiance = models.TextField(verbose_name=_(u"Ambiance"), blank=True, db_column='ambiance',
                                help_text=_(u"Main attraction and interest"))
    access = models.TextField(verbose_name=_(u"Access"), blank=True, db_column='acces',
                              help_text=_(u"Best way to go"))
    disabled_infrastructure = models.TextField(verbose_name=_(u"Disabled infrastructure"), db_column='handicap',
                                               blank=True, help_text=_(u"Any specific infrastructure"))
    duration = models.FloatField(verbose_name=_(u"Duration"), default=0, blank=True, db_column='duree',
                                 help_text=_(u"In decimal hours (ex. 1.5 for 1 h 30)"),
                                 validators=[MinValueValidator(0)])
    is_park_centered = models.BooleanField(verbose_name=_(u"Is in the midst of the park"), db_column='coeur',
                                           help_text=_(u"Crosses center of park"))
    advised_parking = models.CharField(verbose_name=_(u"Advised parking"), max_length=128, blank=True, db_column='parking',
                                       help_text=_(u"Where to park"))
    parking_location = models.PointField(verbose_name=_(u"Parking location"), db_column='geom_parking',
                                         srid=settings.SRID, spatial_index=False, blank=True, null=True)
    public_transport = models.TextField(verbose_name=_(u"Public transport"), blank=True, db_column='transport',
                                        help_text=_(u"Train, bus (see web links)"))
    advice = models.TextField(verbose_name=_(u"Advice"), blank=True, db_column='recommandation',
                              help_text=_(u"Risks, danger, best period, ..."))
    themes = models.ManyToManyField(Theme, related_name="treks",
                                    db_table="o_r_itineraire_theme", blank=True, null=True, verbose_name=_(u"Themes"),
                                    help_text=_(u"Main theme(s)"))
    networks = models.ManyToManyField('TrekNetwork', related_name="treks",
                                      db_table="o_r_itineraire_reseau", blank=True, null=True, verbose_name=_(u"Networks"),
                                      help_text=_(u"Hiking networks"))
    practice = models.ForeignKey('Practice', related_name="treks",
                                 blank=True, null=True, verbose_name=_(u"Practice"), db_column='pratique')
    accessibilities = models.ManyToManyField('Accessibility', related_name="treks",
                                             db_table="o_r_itineraire_accessibilite", blank=True, null=True,
                                             verbose_name=_(u"Accessibilities"))
    route = models.ForeignKey('Route', related_name='treks',
                              blank=True, null=True, verbose_name=_(u"Route"), db_column='parcours')
    difficulty = models.ForeignKey('DifficultyLevel', related_name='treks',
                                   blank=True, null=True, verbose_name=_(u"Difficulty"), db_column='difficulte')
    web_links = models.ManyToManyField('WebLink', related_name="treks",
                                       db_table="o_r_itineraire_web", blank=True, null=True, verbose_name=_(u"Web links"),
                                       help_text=_(u"External resources"))
    related_treks = models.ManyToManyField('self', through='TrekRelationship',
                                           verbose_name=_(u"Related treks"), symmetrical=False,
                                           help_text=_(u"Connections between treks"),
                                           related_name='related_treks+')  # Hide reverse attribute
    parent = models.ForeignKey('self', verbose_name=_(u"Parent"), db_column='parent', blank=True, null=True,
                               related_name='children')
    information_desks = models.ManyToManyField(tourism_models.InformationDesk,
                                               db_table="o_r_itineraire_renseignement", blank=True, null=True,
                                               verbose_name=_(u"Information desks"),
                                               help_text=_(u"Where to obtain information"))
    points_reference = models.MultiPointField(verbose_name=_(u"Points of reference"), db_column='geom_points_reference',
                                              srid=settings.SRID, spatial_index=False, blank=True, null=True)
    source = models.ManyToManyField('common.RecordSource',
                                    null=True, blank=True, related_name='treks',
                                    verbose_name=_("Source"), db_table='o_r_itineraire_source')
    eid = models.CharField(verbose_name=_(u"External id"), max_length=128, blank=True, db_column='id_externe')
    eid2 = models.CharField(verbose_name=_(u"Second external id"), max_length=128, blank=True, db_column='id_externe2')

    objects = Topology.get_manager_cls(models.GeoManager)()

    category_id_prefix = 'T'

    class Meta:
        db_table = 'o_t_itineraire'
        verbose_name = _(u"Trek")
        verbose_name_plural = _(u"Treks")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_document_public_url(self):
        """ Override ``geotrek.common.mixins.PublishableMixin``
        """
        return ('trekking:trek_document_public', [str(self.pk)])

    @property
    def related(self):
        return self.related_treks.exclude(deleted=True).exclude(pk=self.pk).distinct()

    @classproperty
    def related_verbose_name(cls):
        return _("Related treks")

    @property
    def relationships(self):
        # Does not matter if a or b
        return TrekRelationship.objects.filter(trek_a=self)

    @property
    def published_relationships(self):
        return self.relationships.filter(trek_b__published=True)

    @property
    def poi_types(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            # Can't use values_list and must add 'ordering' because of bug:
            # https://code.djangoproject.com/ticket/14930
            values = self.pois.values('ordering', 'type')
        else:
            values = self.pois.values('type')
        pks = [value['type'] for value in values]
        return POIType.objects.filter(pk__in=set(pks))

    @property
    def length_kilometer(self):
        return "%.1f" % (self.length / 1000.0)

    @property
    def networks_display(self):
        return ', '.join([unicode(n) for n in self.networks.all()])

    @property
    def districts_display(self):
        return ', '.join([unicode(d) for d in self.districts])

    @property
    def themes_display(self):
        return ', '.join([unicode(n) for n in self.themes.all()])

    @property
    def city_departure(self):
        cities = self.cities
        return unicode(cities[0]) if len(cities) > 0 else ''

    def kml(self):
        """ Exports trek into KML format, add geometry as linestring and POI
        as place marks """
        kml = simplekml.Kml()
        # Main itinerary
        geom3d = self.geom_3d.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newlinestring(name=self.name,
                                 description=plain_text(self.description),
                                 coords=geom3d.coords)
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        # Place marks
        for poi in self.pois:
            place = poi.geom_3d.transform(settings.API_SRID, clone=True)
            kml.newpoint(name=poi.name,
                         description=plain_text(poi.description),
                         coords=[place.coords])
        return kml._genkml()

    def has_geom_valid(self):
        """A trek should be a LineString, even if it's a loop.
        """
        return super(Trek, self).has_geom_valid() and self.geom.geom_type.lower() == 'linestring'

    @property
    def duration_pretty(self):
        return trekking_tags.duration(self.duration)

    @classproperty
    def duration_pretty_verbose_name(cls):
        return _("Formated duration")

    @classmethod
    def path_treks(cls, path):
        treks = cls.objects.existing().filter(aggregations__path=path)
        # The following part prevents conflict with default trek ordering
        # ProgrammingError: SELECT DISTINCT ON expressions must match initial ORDER BY expressions
        return treks.order_by('topo_object').distinct('topo_object')

    @classmethod
    def topology_treks(cls, topology):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = cls.objects.existing().filter(geom__intersects=area)
        return qs

    @classmethod
    def published_topology_treks(cls, topology):
        return cls.topology_treks(topology).filter(published=True)

    # Rando v1 compat
    @property
    def usages(self):
        return [self.practice] if self.practice else []

    @classmethod
    def get_create_label(cls):
        return _(u"Add a new trek")

    @property
    def published_children_id(self):
        return self.children.filter(published=True).values_list('id', flat=True)

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError(_(u"Cannot use itself as parent trek."))
        if self.parent and self.parent.parent:
            raise ValidationError(_(u"Cannot use a a child trek as parent trek."))

    @property
    def prefixed_category_id(self):
        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE and self.practice:
            return '{prefix}{id}'.format(prefix=self.category_id_prefix, id=self.practice.id)
        else:
            return self.category_id_prefix

Path.add_property('treks', Trek.path_treks, _(u"Treks"))
Topology.add_property('treks', Trek.topology_treks, _(u"Treks"))
Topology.add_property('published_treks', lambda self: intersecting(Trek, self, distance=settings.TOURISM_INTERSECTION_MARGIN).filter(published=True), _(u"Published treks"))
Intervention.add_property('treks', lambda self: self.topology.treks if self.topology else [], _(u"Treks"))
Project.add_property('treks', lambda self: self.edges_by_attr('treks'), _(u"Treks"))
tourism_models.TouristicContent.add_property('treks', lambda self: intersecting(Trek, self, distance=settings.TOURISM_INTERSECTION_MARGIN), _(u"Treks"))
tourism_models.TouristicContent.add_property('published_treks', lambda self: intersecting(Trek, self, distance=settings.TOURISM_INTERSECTION_MARGIN).filter(published=True), _(u"Published treks"))
tourism_models.TouristicEvent.add_property('treks', lambda self: intersecting(Trek, self, distance=settings.TOURISM_INTERSECTION_MARGIN), _(u"Treks"))
tourism_models.TouristicEvent.add_property('published_treks', lambda self: intersecting(Trek, self, distance=settings.TOURISM_INTERSECTION_MARGIN).filter(published=True), _(u"Published treks"))


class TrekRelationshipManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        qs = super(TrekRelationshipManager, self).get_queryset().select_related('trek_a', 'trek_b')
        # Exclude deleted treks
        return qs.exclude(trek_a__deleted=True).exclude(trek_b__deleted=True)


class TrekRelationship(models.Model):
    """
    Relationships between treks : symmetrical aspect is managed by a trigger that
    duplicates all couples (trek_a, trek_b)
    """
    has_common_departure = models.BooleanField(verbose_name=_(u"Common departure"), db_column='depart_commun', default=False)
    has_common_edge = models.BooleanField(verbose_name=_(u"Common edge"), db_column='troncons_communs', default=False)
    is_circuit_step = models.BooleanField(verbose_name=_(u"Circuit step"), db_column='etape_circuit', default=False)

    trek_a = models.ForeignKey(Trek, related_name="trek_relationship_a", db_column='itineraire_a')
    trek_b = models.ForeignKey(Trek, related_name="trek_relationship_b", db_column='itineraire_b', verbose_name=_(u"Trek"))

    objects = TrekRelationshipManager()

    class Meta:
        db_table = 'o_r_itineraire_itineraire'
        verbose_name = _(u"Trek relationship")
        verbose_name_plural = _(u"Trek relationships")
        unique_together = ('trek_a', 'trek_b')

    def __unicode__(self):
        return u"%s <--> %s" % (self.trek_a, self.trek_b)

    @property
    def relation(self):
        return u"%s %s%s%s" % (
            self.trek_b.name_display,
            _("Departure") if self.has_common_departure else '',
            _("Path") if self.has_common_edge else '',
            _("Circuit") if self.is_circuit_step else ''
        )

    @property
    def relation_display(self):
        return self.relation


class TrekNetwork(PictogramMixin):

    network = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='reseau')

    class Meta:
        db_table = 'o_b_reseau'
        verbose_name = _(u"Trek network")
        verbose_name_plural = _(u"Trek networks")
        ordering = ['network']

    def __unicode__(self):
        return self.network


class Practice(PictogramMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    cirkwi = models.ForeignKey('cirkwi.CirkwiLocomotion', verbose_name=_(u"Cirkwi locomotion"), null=True, blank=True)

    class Meta:
        db_table = 'o_b_pratique'
        verbose_name = _(u"Practice")
        verbose_name_plural = _(u"Practices")
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Accessibility(OptionalPictogramMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    cirkwi = models.ForeignKey('cirkwi.CirkwiTag', verbose_name=_(u"Cirkwi tag"), null=True, blank=True)

    id_prefix = 'A'

    class Meta:
        db_table = 'o_b_accessibilite'
        verbose_name = _(u"Accessibility")
        verbose_name_plural = _(u"Accessibilities")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def prefixed_id(self):
        return '{prefix}{id}'.format(prefix=self.id_prefix, id=self.id)


class Route(OptionalPictogramMixin):

    route = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='parcours')

    class Meta:
        db_table = 'o_b_parcours'
        verbose_name = _(u"Route")
        verbose_name_plural = _(u"Routes")
        ordering = ['route']

    def __unicode__(self):
        return self.route


class DifficultyLevel(OptionalPictogramMixin):

    """We use an IntegerField for id, since we want to edit it in Admin.
    This column is used to order difficulty levels, especially in public website
    where treks are filtered by difficulty ids.
    """
    id = models.IntegerField(primary_key=True)
    difficulty = models.CharField(verbose_name=_(u"Difficulty level"),
                                  max_length=128, db_column='difficulte')
    cirkwi_level = models.IntegerField(verbose_name=_(u"Cirkwi level"), blank=True, null=True,
                                       db_column='niveau_cirkwi', help_text=_(u"Between 1 and 8"))
    cirkwi = models.ForeignKey('cirkwi.CirkwiTag', verbose_name=_(u"Cirkwi tag"), null=True, blank=True)

    class Meta:
        db_table = 'o_b_difficulte'
        verbose_name = _(u"Difficulty level")
        verbose_name_plural = _(u"Difficulty levels")
        ordering = ['id']

    def __unicode__(self):
        return self.difficulty

    def save(self, *args, **kwargs):
        """Manually auto-increment ids"""
        if not self.id:
            try:
                last = self.__class__.objects.all().order_by('-id')[0]
                self.id = last.id + 1
            except IndexError:
                self.id = 1
        super(DifficultyLevel, self).save(*args, **kwargs)


class WebLinkManager(models.Manager):
    def get_queryset(self):
        return super(WebLinkManager, self).get_queryset().select_related('category')


class WebLink(models.Model):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    url = models.URLField(verbose_name=_(u"URL"), max_length=128, db_column='url')
    category = models.ForeignKey('WebLinkCategory', verbose_name=_(u"Category"),
                                 related_name='links', null=True, blank=True,
                                 db_column='categorie')

    objects = WebLinkManager()

    class Meta:
        db_table = 'o_t_web'
        verbose_name = _(u"Web link")
        verbose_name_plural = _(u"Web links")
        ordering = ['name']

    def __unicode__(self):
        category = "%s - " % self.category.label if self.category else ""
        return u"%s%s (%s)" % (category, self.name, self.url)

    @classmethod
    @models.permalink
    def get_add_url(cls):
        return ('trekking:weblink_add', )


class WebLinkCategory(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')

    class Meta:
        db_table = 'o_b_web_category'
        verbose_name = _(u"Web link category")
        verbose_name_plural = _(u"Web link categories")
        ordering = ['label']

    def __unicode__(self):
        return u"%s" % self.label


class POIManager(models.GeoManager):
    def get_queryset(self):
        return super(POIManager, self).get_queryset().select_related('type', 'structure')


class POI(StructureRelated, PicturesMixin, PublishableMixin, MapEntityMixin, Topology):

    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    description = models.TextField(verbose_name=_(u"Description"), db_column='description',
                                   help_text=_(u"History, details,  ..."))
    type = models.ForeignKey('POIType', related_name='pois', verbose_name=_(u"Type"), db_column='type')
    eid = models.CharField(verbose_name=_(u"External id"), max_length=128, blank=True, db_column='id_externe')

    class Meta:
        db_table = 'o_t_poi'
        verbose_name = _(u"POI")
        verbose_name_plural = _(u"POI")

    # Override default manager
    objects = Topology.get_manager_cls(POIManager)()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.type)

    @models.permalink
    def get_document_public_url(self):
        """ Override ``geotrek.common.mixins.PublishableMixin``
        """
        return ('trekking:poi_document_public', [str(self.pk)])

    def save(self, *args, **kwargs):
        super(POI, self).save(*args, **kwargs)
        # Invalidate treks map
        for trek in self.treks.all():
            try:
                os.remove(trek.get_map_image_path())
            except OSError:
                pass

    @property
    def type_display(self):
        return unicode(self.type)

    @property
    def serializable_type(self):
        return {'label': self.type.label,
                'pictogram': self.type.get_pictogram_url()}

    @classmethod
    def path_pois(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_pois(cls, topology):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology)
        else:
            area = topology.geom.buffer(settings.TREK_POI_INTERSECTION_MARGIN)
            qs = cls.objects.existing().filter(geom__intersects=area)
        return qs

    @classmethod
    def published_topology_pois(cls, topology):
        return cls.topology_pois(topology).filter(published=True)

Path.add_property('pois', POI.path_pois, _(u"POIs"))
Topology.add_property('pois', POI.topology_pois, _(u"POIs"))
Topology.add_property('published_pois', POI.published_topology_pois, _(u"Published POIs"))
Intervention.add_property('pois', lambda self: self.topology.pois if self.topology else [], _(u"POIs"))
Project.add_property('pois', lambda self: self.edges_by_attr('pois'), _(u"POIs"))
tourism_models.TouristicContent.add_property('pois', lambda self: intersecting(POI, self, distance=settings.TOURISM_INTERSECTION_MARGIN), _(u"POIs"))
tourism_models.TouristicContent.add_property('published_pois', lambda self: intersecting(POI, self, distance=settings.TOURISM_INTERSECTION_MARGIN).filter(published=True), _(u"Published POIs"))
tourism_models.TouristicEvent.add_property('pois', lambda self: intersecting(POI, self, distance=settings.TOURISM_INTERSECTION_MARGIN), _(u"POIs"))
tourism_models.TouristicEvent.add_property('published_pois', lambda self: intersecting(POI, self, distance=settings.TOURISM_INTERSECTION_MARGIN).filter(published=True), _(u"Published POIs"))


class POIType(PictogramMixin):

    label = models.CharField(verbose_name=_(u"Label"), max_length=128, db_column='nom')
    cirkwi = models.ForeignKey('cirkwi.CirkwiPOICategory', verbose_name=_(u"Cirkwi POI category"), null=True, blank=True)

    class Meta:
        db_table = 'o_b_poi'
        verbose_name = _(u"POI type")
        verbose_name_plural = _(u"POI types")
        ordering = ['label']

    def __unicode__(self):
        return self.label
