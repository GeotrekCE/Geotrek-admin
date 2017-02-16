# -*- coding: utf-8 -*-
import logging
import functools

from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import fromstr, LineString

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import (TimeStampedModelMixin, NoDeleteMixin,
                                   AddPropertyMixin)
from geotrek.common.utils import classproperty
from geotrek.common.utils.postgresql import debug_pg_notices
from geotrek.altimetry.models import AltimetryMixin

from .helpers import PathHelper, TopologyHelper
from django.db import connections, DEFAULT_DB_ALIAS


logger = logging.getLogger(__name__)


class PathManager(models.GeoManager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible.
        """
        return super(PathManager, self).get_queryset().filter(visible=True)


class PathInvisibleManager(models.GeoManager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(PathInvisibleManager, self).get_queryset()

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).


class Path(AddPropertyMixin, MapEntityMixin, AltimetryMixin,
           TimeStampedModelMixin, StructureRelated):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=False)
    geom_cadastre = models.LineStringField(null=True, srid=settings.SRID, spatial_index=False,
                                           editable=False)
    valid = models.BooleanField(db_column='valide', default=True, verbose_name=_(u"Validity"),
                                help_text=_(u"Approved by manager"))
    visible = models.BooleanField(db_column='visible', default=True, verbose_name=_(u"Visible"),
                                  help_text=_(u"Shown in lists and maps"))
    name = models.CharField(null=True, blank=True, max_length=20, db_column='nom', verbose_name=_(u"Name"),
                            help_text=_(u"Official name"))
    comments = models.TextField(null=True, blank=True, db_column='remarques', verbose_name=_(u"Comments"),
                                help_text=_(u"Remarks"))

    departure = models.CharField(null=True, blank=True, default="", max_length=250, db_column='depart', verbose_name=_(u"Departure"),
                                 help_text=_(u"Departure place"))
    arrival = models.CharField(null=True, blank=True, default="", max_length=250, db_column='arrivee', verbose_name=_(u"Arrival"),
                               help_text=_(u"Arrival place"))

    comfort = models.ForeignKey('Comfort',
                                null=True, blank=True, related_name='paths',
                                verbose_name=_("Comfort"), db_column='confort')
    source = models.ForeignKey('PathSource',
                               null=True, blank=True, related_name='paths',
                               verbose_name=_("Source"), db_column='source')
    stake = models.ForeignKey('Stake',
                              null=True, blank=True, related_name='paths',
                              verbose_name=_("Maintenance stake"), db_column='enjeu')
    usages = models.ManyToManyField('Usage',
                                    blank=True, null=True, related_name="paths",
                                    verbose_name=_(u"Usages"), db_table="l_r_troncon_usage")
    networks = models.ManyToManyField('Network',
                                      blank=True, null=True, related_name="paths",
                                      verbose_name=_(u"Networks"), db_table="l_r_troncon_reseau")
    eid = models.CharField(verbose_name=_(u"External id"), max_length=128, blank=True, null=True, db_column='id_externe')

    objects = PathManager()
    include_invisible = PathInvisibleManager()

    is_reversed = False

    @property
    def length_2d(self):
        if self.geom:
            return round(self.geom.length, 1)
        else:
            return None

    @classproperty
    def length_2d_verbose_name(cls):
        return _(u"2D Length")

    @property
    def length_2d_display(self):
        return self.length_2d

    def __unicode__(self):
        return self.name or _('path %d') % self.pk

    class Meta:
        db_table = 'l_t_troncon'
        verbose_name = _(u"Path")
        verbose_name_plural = _(u"Paths")

    @classmethod
    def closest(cls, point):
        """
        Returns the closest path of the point.
        Will fail if no path in database.
        """
        # TODO: move to custom manager
        if point.srid != settings.SRID:
            point = point.transform(settings.SRID, clone=True)
        return cls.objects.all().exclude(visible=False).distance(point).order_by('distance')[0]

    def is_overlap(self):
        return not PathHelper.disjoint(self.geom, self.pk)

    def reverse(self):
        """
        Reverse the geometry.
        We keep track of this, since we will have to work on topologies at save()
        """
        reversed_coord = self.geom.coords[-1::-1]
        self.geom = LineString(reversed_coord)
        self.is_reversed = True
        return self

    def interpolate(self, point):
        """
        Returns position ([0.0-1.0]) and offset (distance) of the point
        along this path.
        """
        return PathHelper.interpolate(self, point)

    def snap(self, point):
        """
        Returns the point snapped (i.e closest) to the path line geometry.
        """
        return PathHelper.snap(self, point)

    def reload(self, fromdb=None):
        # Update object's computed values (reload from database)
        if self.pk and self.visible:
            fromdb = self.__class__.objects.get(pk=self.pk)
            self.geom = fromdb.geom
            AltimetryMixin.reload(self, fromdb)
            TimeStampedModelMixin.reload(self, fromdb)
        return self

    @debug_pg_notices
    def save(self, *args, **kwargs):
        # If the path was reversed, we have to invert related topologies
        if self.is_reversed:
            for aggr in self.aggregations.all():
                aggr.start_position = 1 - aggr.start_position
                aggr.end_position = 1 - aggr.end_position
                aggr.save()
            self._is_reversed = False
        super(Path, self).save(*args, **kwargs)
        self.reload()

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                  self.get_detail_url(),
                                                                  self,
                                                                  self)

    @property
    def name_csv_display(self):
        return unicode(self)

    @classproperty
    def trails_verbose_name(cls):
        return _("Trails")

    @property
    def trails_display(self):
        trails = getattr(self, '_trails', self.trails)
        if trails:
            return ", ".join([t.name_display for t in trails])
        return _("None")

    @property
    def trails_csv_display(self):
        trails = getattr(self, '_trails', self.trails)
        if trails:
            return ", ".join([unicode(t) for t in trails])
        return _("None")

    @classmethod
    def get_create_label(cls):
        return _(u"Add a new path")

    @property
    def checkbox(self):
        return u'<input type="checkbox" name="{}[]" value="{}" />'.format('path',
                                                                          self.pk)

    @classproperty
    def checkbox_verbose_name(cls):
        return _("Action")

    @property
    def checkbox_display(self):
        return self.checkbox

    def merge_path(self, path_to_merge):
        """
        Path unification
        :param path_to path_to_merge: Path instance to merge
        :return: Boolean
        """
        if (self.pk and path_to_merge) and (self.pk != path_to_merge.pk):
            conn = connections[DEFAULT_DB_ALIAS]
            cursor = conn.cursor()
            sql = "SELECT ft_merge_path({}, {});".format(self.pk, path_to_merge.pk)
            cursor.execute(sql)

            result = cursor.fetchall()[0][0]

            if result:
                # reload object after unification
                self.reload()

            return result


class Topology(AddPropertyMixin, AltimetryMixin, TimeStampedModelMixin, NoDeleteMixin):
    paths = models.ManyToManyField(Path, db_column='troncons', through='PathAggregation', verbose_name=_(u"Path"))
    offset = models.FloatField(default=0.0, db_column='decallage', verbose_name=_(u"Offset"))  # in SRID units
    kind = models.CharField(editable=False, verbose_name=_(u"Kind"), max_length=32)

    # Override default manager
    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    geom = models.GeometryField(editable=(not settings.TREKKING_TOPOLOGY_ENABLED),
                                srid=settings.SRID, null=True,
                                default=None, spatial_index=False)

    """ Fake srid attribute, that prevents transform() calls when using Django map widgets. """
    srid = settings.API_SRID

    class Meta:
        db_table = 'e_t_evenement'
        verbose_name = _(u"Topology")
        verbose_name_plural = _(u"Topologies")

    def __init__(self, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        if not self.pk:
            self.kind = self.__class__.KIND

    @property
    def length_2d(self):
        if self.geom and not self.ispoint():
            return round(self.geom.length, 1)

        else:
            return None

    @classproperty
    def length_2d_verbose_name(cls):
        return _(u"2D Length")

    @property
    def length_2d_display(self):
        return self.length_2d

    @classproperty
    def KIND(cls):
        return cls._meta.object_name.upper()

    def __unicode__(self):
        return u"%s (%s)" % (_(u"Topology"), self.pk)

    def ispoint(self):
        if not settings.TREKKING_TOPOLOGY_ENABLED or not self.pk:
            return self.geom and self.geom.geom_type == 'Point'
        return all([a.start_position == a.end_position for a in self.aggregations.all()])

    def add_path(self, path, start=0.0, end=1.0, order=0, reload=True):
        """
        Shortcut function to add paths into this topology.
        """
        from .factories import PathAggregationFactory
        aggr = PathAggregationFactory.create(topo_object=self,
                                             path=path,
                                             start_position=start,
                                             end_position=end,
                                             order=order)

        if self.deleted:
            self.deleted = False
            self.save(update_fields=['deleted'])

        # Since a trigger modifies geom, we reload the object
        if reload:
            self.reload()
        return aggr

    @classmethod
    def overlapping(cls, topologies):
        """ Return a Topology queryset overlapping specified topologies.
        """
        return TopologyHelper.overlapping(cls, topologies)

    def mutate(self, other, delete=True):
        """
        Take alls attributes of the other topology specified and
        save them into this one. Optionnally deletes the other.
        """
        self.offset = other.offset
        self.save(update_fields=['offset'])
        PathAggregation.objects.filter(topo_object=self).delete()
        # The previous operation has put deleted = True (in triggers)
        # and NULL in geom (see update_geometry_of_evenement:: IF t_count = 0)
        self.deleted = False
        self.geom = other.geom
        self.save(update_fields=['deleted', 'geom'])

        # Now copy all agregations from other to self
        aggrs = other.aggregations.all()
        # A point has only one aggregation, except if it is on an intersection.
        # In this case, the trigger will create them, so ignore them here.
        if other.ispoint():
            aggrs = aggrs[:1]
        for aggr in aggrs:
            self.add_path(aggr.path, aggr.start_position, aggr.end_position, aggr.order, reload=False)
        self.reload()
        if delete:
            other.delete(force=True)  # Really delete it from database
        return self

    def reload(self, fromdb=None):
        """
        Reload into instance all computed attributes in triggers.
        """
        if self.pk:
            # Update computed values
            fromdb = self.__class__.objects.get(pk=self.pk)
            self.geom = fromdb.geom
            # /!\ offset may be set by a trigger OR in
            # the django code, reload() will override
            # any unsaved value
            self.offset = fromdb.offset
            AltimetryMixin.reload(self, fromdb)
            TimeStampedModelMixin.reload(self, fromdb)
            NoDeleteMixin.reload(self, fromdb)

        return self

    @debug_pg_notices
    def save(self, *args, **kwargs):
        # HACK: these fields are readonly from the Django point of view
        # but they can be changed at DB level. Since Django write all fields
        # to DB anyway, it is important to update it before writting
        if self.pk and settings.TREKKING_TOPOLOGY_ENABLED:
            existing = self.__class__.objects.get(pk=self.pk)
            self.length = existing.length
            # In the case of points, the geom can be set by Django. Don't override.
            point_geom_not_set = self.ispoint() and self.geom is None
            geom_already_in_db = not self.ispoint() and existing.geom is not None
            if (point_geom_not_set or geom_already_in_db):
                self.geom = existing.geom
        else:
            if not self.deleted and self.geom is None:
                # We cannot have NULL geometry. So we use an empty one,
                # it will be computed or overwritten by triggers.
                self.geom = fromstr('POINT (0 0)')

        if not self.kind:
            if self.KIND == "TOPOLOGYMIXIN":
                raise Exception("Cannot save abstract topologies")
            self.kind = self.__class__.KIND

        # Static value for Topology offset, if any
        shortmodelname = self._meta.object_name.lower().replace('edge', '')
        self.offset = settings.TOPOLOGY_STATIC_OFFSETS.get(shortmodelname, self.offset)

        # Save into db
        super(Topology, self).save(*args, **kwargs)
        self.reload()

    def serialize(self, **kwargs):
        return TopologyHelper.serialize(self, **kwargs)

    @classmethod
    def deserialize(cls, serialized):
        return TopologyHelper.deserialize(serialized)

    def distance(self, to_cls):
        """Distance to associate this topology to another topology class"""
        return None


class PathAggregationManager(models.GeoManager):
    def get_queryset(self):
        return super(PathAggregationManager, self).get_queryset().order_by('order')


class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False, db_column='troncon',
                             verbose_name=_(u"Path"),
                             related_name="aggregations",
                             on_delete=models.DO_NOTHING)  # The CASCADE behavior is enforced at DB-level (see file ../sql/20_evenements_troncons.sql)
    topo_object = models.ForeignKey(Topology, null=False, related_name="aggregations",
                                    db_column='evenement', verbose_name=_(u"Topology"))
    start_position = models.FloatField(db_column='pk_debut', verbose_name=_(u"Start position"), db_index=True)
    end_position = models.FloatField(db_column='pk_fin', verbose_name=_(u"End position"), db_index=True)
    order = models.IntegerField(db_column='ordre', default=0, blank=True, null=True, verbose_name=_(u"Order"))

    # Override default manager
    objects = PathAggregationManager()

    def __unicode__(self):
        return u"%s (%s-%s: %s - %s)" % (_("Path aggregation"), self.path.pk, self.path.name, self.start_position, self.end_position)

    @property
    def start_meter(self):
        try:
            return 0 if self.start_position == 0.0 else int(self.start_position * self.path.length)
        except ValueError:
            return -1

    @property
    def end_meter(self):
        try:
            return 0 if self.end_position == 0.0 else int(self.end_position * self.path.length)
        except ValueError:
            return -1

    @property
    def is_full(self):
        return (self.start_position == 0.0 and self.end_position == 1.0 or
                self.start_position == 1.0 and self.end_position == 0.0)

    @debug_pg_notices
    def save(self, *args, **kwargs):
        return super(PathAggregation, self).save(*args, **kwargs)

    class Meta:
        db_table = 'e_r_evenement_troncon'
        verbose_name = _(u"Path aggregation")
        verbose_name_plural = _(u"Path aggregations")
        # Important - represent the order of the path in the Topology path list
        ordering = ['order', ]


class PathSource(StructureRelated):

    source = models.CharField(verbose_name=_(u"Source"), max_length=50)

    class Meta:
        db_table = 'l_b_source_troncon'
        verbose_name = _(u"Path source")
        verbose_name_plural = _(u"Path sources")
        ordering = ['source']

    def __unicode__(self):
        return self.source


@functools.total_ordering
class Stake(StructureRelated):

    stake = models.CharField(verbose_name=_(u"Stake"), max_length=50, db_column='enjeu')

    class Meta:
        db_table = 'l_b_enjeu'
        verbose_name = _(u"Maintenance stake")
        verbose_name_plural = _(u"Maintenance stakes")
        ordering = ['id']

    def __lt__(self, other):
        if other is None:
            return False
        return self.pk < other.pk

    def __eq__(self, other):
        return isinstance(other, Stake) \
            and self.pk == other.pk

    def __unicode__(self):
        return self.stake


class Comfort(StructureRelated):

    comfort = models.CharField(verbose_name=_(u"Comfort"), max_length=50, db_column='confort')

    class Meta:
        db_table = 'l_b_confort'
        verbose_name = _(u"Comfort")
        verbose_name_plural = _(u"Comforts")
        ordering = ['comfort']

    def __unicode__(self):
        return self.comfort


class Usage(StructureRelated):

    usage = models.CharField(verbose_name=_(u"Usage"), max_length=50, db_column='usage')

    class Meta:
        db_table = 'l_b_usage'
        verbose_name = _(u"Usage")
        verbose_name_plural = _(u"Usages")
        ordering = ['usage']

    def __unicode__(self):
        return self.usage


class Network(StructureRelated):

    network = models.CharField(verbose_name=_(u"Network"), max_length=50, db_column='reseau')

    class Meta:
        db_table = 'l_b_reseau'
        verbose_name = _(u"Network")
        verbose_name_plural = _(u"Networks")
        ordering = ['network']

    def __unicode__(self):
        return self.network


class Trail(MapEntityMixin, Topology, StructureRelated):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    name = models.CharField(verbose_name=_(u"Name"), max_length=64, db_column='nom')
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=64, db_column='depart')
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=64, db_column='arrivee')
    comments = models.TextField(default="", blank=True, verbose_name=_(u"Comments"), db_column='commentaire')

    class Meta:
        db_table = 'l_t_sentier'
        verbose_name = _(u"Trail")
        verbose_name_plural = _(u"Trails")
        ordering = ['name']

    objects = Topology.get_manager_cls(models.GeoManager)()

    def __unicode__(self):
        return self.name

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                  self.get_detail_url(),
                                                                  self,
                                                                  self)

    @classmethod
    def path_trails(cls, path):
        return cls.objects.existing().filter(aggregations__path=path)


Path.add_property('trails', lambda self: Trail.path_trails(self), _(u"Trails"))
Topology.add_property('trails', lambda self: Trail.overlapping(self), _(u"Trails"))
