# -*- coding: utf-8 -*-
import re
from math import isnan
import logging
from datetime import datetime
import functools

from django.contrib.gis.db import models
from django.db import connection
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import LineString, Point

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.common.models import TimeStampedModel, NoDeleteMixin
from geotrek.common.utils import classproperty

from .helpers import PathHelper, TopologyHelper


logger = logging.getLogger(__name__)


class AltimetryMixin(models.Model):
    # Computed values (managed at DB-level with triggers)
    length = models.FloatField(editable=False, default=0.0, null=True, blank=True, db_column='longueur', verbose_name=_(u"Length"))
    ascent = models.IntegerField(editable=False, default=0, null=True, blank=True, db_column='denivelee_positive', verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, null=True, blank=True, db_column='denivelee_negative', verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, null=True, blank=True, db_column='altitude_minimum', verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, null=True, blank=True, db_column='altitude_maximum', verbose_name=_(u"Maximum elevation"))
    slope = models.FloatField(editable=False, null=True, blank=True, default=0.0, verbose_name=_(u"Slope"), db_column='pente')

    COLUMNS = ['length', 'ascent', 'descent', 'min_elevation', 'max_elevation', 'slope']

    class Meta:
        abstract = True

    def get_elevation_profile(self):
        """
        Extract elevation profile from geom.
        """
        return AltimetryMixin.elevation_profile(self.geom)

    @staticmethod
    def elevation_profile(geometry, precision=None, offset=0):
        """Extract elevation profile from a 3D geometry.

        :precision:  geometry sampling in meters
        """
        precision = precision or settings.ALTIMETRIC_PROFILE_PRECISION

        if geometry.geom_type == 'MultiLineString':
            profile = []
            for subcoords in geometry.coords:
                subline = LineString(subcoords)
                offset += subline.length
                subprofile = AltimetryMixin.elevation_profile(subline, precision, offset)
                profile.extend(subprofile)
            return profile

        sql = """
        SELECT (%(offset)s + distance) as abscissa,
               ST_X(ST_Transform(geom, %(api_srid)s)) as lng,
               ST_Y(ST_Transform(geom, %(api_srid)s)) as lat,
               ST_Z(geom) as h
        FROM ft_drape_line('%(ewkt)s'::geometry, %(precision)s)
        ORDER BY abscissa
        """ % {'offset': offset, 'api_srid': settings.API_SRID, 'ewkt': geometry.ewkt, 'precision': precision}
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).

class Path(MapEntityMixin, AltimetryMixin, TimeStampedModel, StructureRelated):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=False,
                                  dim=3)
    geom_cadastre = models.LineStringField(null=True, srid=settings.SRID,
                                           spatial_index=False, dim=3)
    valid = models.BooleanField(db_column='valide', default=True, verbose_name=_(u"Validity"),
                                help_text=_(u"Approved by manager"))
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

    # Override default manager
    objects = models.GeoManager()

    trail = models.ForeignKey('Trail',
                              null=True, blank=True, related_name='paths',
                              verbose_name=_("Trail"), db_column='sentier')
    datasource = models.ForeignKey('Datasource',
                                   null=True, blank=True, related_name='paths',
                                   verbose_name=_("Datasource"), db_column='source')
    stake = models.ForeignKey('Stake',
                              null=True, blank=True, related_name='paths',
                              verbose_name=_("Stake"), db_column='enjeu')
    usages = models.ManyToManyField('Usage',
                                    blank=True, null=True, related_name="paths",
                                    verbose_name=_(u"Usages"), db_table="l_r_troncon_usage")
    networks = models.ManyToManyField('Network',
                                      blank=True, null=True, related_name="paths",
                                      verbose_name=_(u"Networks"), db_table="l_r_troncon_reseau")

    is_reversed = False

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
        return cls.objects.all().distance(point).order_by('distance')[0]

    def is_overlap(self):
        return not PathHelper.disjoint(self.geom, self.pk)

    def reverse(self):
        """
        Reverse the geometry.
        We keep track of this, since we will have to work on topologies at save()
        """
        # path.geom.reverse() won't work for 3D coords
        reversed_coord = self.geom.coords[-1::-1]
        # TODO: Why do we have to filter nan variable ?! Why are they here in the first place ?
        valid_coords = [(x, y, 0.0 if isnan(z) else z) for x, y, z in reversed_coord]
        self.geom = LineString(valid_coords)
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

    def reload(self):
        # Update object's computed values (reload from database)
        tmp = self.__class__.objects.get(pk=self.pk)
        self.date_insert = tmp.date_insert
        self.date_update = tmp.date_update
        self.length = tmp.length
        self.slope = tmp.slope
        self.ascent = tmp.ascent
        self.descent = tmp.descent
        self.min_elevation = tmp.min_elevation
        self.max_elevation = tmp.max_elevation
        self.geom = tmp.geom

    def delete(self, using=None):
        """
        Since Path is not a NoDeleteMixin, a deletion does not change latest_updated
        and cache is not refreshed.
        TODO : one day, Path should be a ``NoDeleteMixin``, remove all of this.
        """
        super(Path, self).delete(using=using)
        try:
            latest = Path.objects.latest("date_update")
            latest.date_update = datetime.now()
            latest.save()
        except Path.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        before = len(connection.connection.notices) if connection.connection else 0
        try:
            # If the path was reversed, we have to invert related topologies
            if self.is_reversed:
                for aggr in self.aggregations.all():
                    aggr.start_position = 1 - aggr.start_position
                    aggr.end_position = 1 - aggr.end_position
                    aggr.save()
                self._is_reversed = False
            super(Path, self).save(*args, **kwargs)
            self.reload()
        finally:
            # Show triggers output
            allnotices = []
            current = ''
            if connection.connection:
                notices = []
                for notice in connection.connection.notices[before:]:
                    try:
                        notice, context = notice.split('CONTEXT:', 1)
                        context = re.sub("\s+", " ", context)
                    except ValueError:
                        context = ''
                    notices.append((context, notice))
                    if context != current:
                        allnotices.append(notices)
                        notices = []
                        current = context
                allnotices.append(notices)
            current = ''
            for notices in allnotices:
                for context, notice in notices:
                    if context != current:
                        if context != '':
                            logger.debug('Context %s...:' % context.strip()[:80])
                        current = context
                    notice = notice.replace('NOTICE: ', '')
                    prefix = '' if context == '' else '        '
                    logger.debug('%s%s' % (prefix, notice.strip()))

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self)

    @property
    def name_csv_display(self):
        return unicode(self)

    @property
    def trail_display(self):
        if self.trail:
            return u'<a data-pk="%s" href="%s" >%s</a>' % (self.trail.pk, self.trail.get_detail_url(), self.trail)
        return _("None")

    @property
    def trail_csv_display(self):
        if self.trail:
            return unicode(self.trail)
        return _("None")


class Topology(AltimetryMixin, TimeStampedModel, NoDeleteMixin):
    paths = models.ManyToManyField(Path, editable=False, db_column='troncons', through='PathAggregation', verbose_name=_(u"Path"))
    offset = models.FloatField(default=0.0, db_column='decallage', verbose_name=_(u"Offset"))  # in SRID units
    kind = models.CharField(editable=False, verbose_name=_(u"Kind"), max_length=32)

    # Override default manager
    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    geom = models.GeometryField(editable=False, srid=settings.SRID, null=True,
                                blank=True, spatial_index=False, dim=3)

    class Meta:
        db_table = 'e_t_evenement'
        verbose_name = _(u"Topology")
        verbose_name_plural = _(u"Topologies")

    def __init__(self, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        if not self.pk:
            self.kind = self.__class__.KIND

    @classmethod
    def add_property(cls, name, func):
        if hasattr(cls, name):
            raise AttributeError("%s has already an attribute %s" % (cls, name))
        setattr(cls, name, property(func))

    @classproperty
    def KIND(cls):
        return cls._meta.object_name.upper()

    def __unicode__(self):
        return u"%s (%s)" % (_(u"Topology"), self.pk)

    def ispoint(self):
        if not self.pk and self.geom and self.geom.geom_type == 'Point':
            return True
        return all([a.start_position == a.end_position for a in self.aggregations.all()])

    def geom_as_point(self):
        geom = self.geom
        assert geom, 'Topology point is None'
        if geom.geom_type != 'Point':
            logger.warning("Topology has wrong geometry type : %s instead of Point" % geom.geom_type)
            geom = Point(geom.coords[0], srid=settings.SRID)
        return geom

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
        self.geom = other.geom
        self.save()
        PathAggregation.objects.filter(topo_object=self).delete()
        aggrs = other.aggregations.all()
        # A point has only one aggregation, except if it is on an intersection.
        # In this case, the trigger will create them, so ignore them here.
        if other.ispoint():
            aggrs = aggrs[:1]
        for aggr in aggrs:
            self.add_path(aggr.path, aggr.start_position, aggr.end_position, aggr.order, reload=False)
        if delete:
            other.delete(force=True)  # Really delete it from database
        self.save()
        return self

    def reload(self):
        """
        Reload into instance all computed attributes in triggers.
        """
        if self.pk:
            # Update computed values
            tmp = self.__class__.objects.get(pk=self.pk)
            self.date_insert = tmp.date_insert
            self.date_update = tmp.date_update
            self.length = tmp.length
            self.slope = tmp.slope
            self.ascent = tmp.ascent
            self.descent = tmp.descent
            self.min_elevation = tmp.min_elevation
            self.max_elevation = tmp.max_elevation
            self.geom = tmp.geom
            self.offset = tmp.offset  # /!\ offset may be set by a trigger OR in
                                      # the django code, reload() will override
                                      # any unsaved value
        return self

    def save(self, *args, **kwargs):
        # HACK: these fields are readonly from the Django point of view
        # but they can be changed at DB level. Since Django write all fields
        # to DB anyway, it is important to update it before writting
        if self.pk:
            tmp = self.__class__.objects.get(pk=self.pk)
            self.length = tmp.length
            # In the case of points, the geom can be set by Django. Don't override.
            if (self.ispoint() and self.geom is None) or \
               (not self.ispoint() and tmp.geom is not None):
                self.geom = tmp.geom

        if not self.kind:
            if self.KIND == "TOPOLOGYMIXIN":
                raise Exception("Cannot save abstract topologies")
            self.kind = self.__class__.KIND

        shortmodelname = self._meta.object_name.lower().replace('edge', '')
        self.offset = settings.TOPOLOGY_STATIC_OFFSETS.get(shortmodelname, self.offset)

        before = len(connection.connection.notices) if connection.connection else 0
        try:
            super(Topology, self).save(*args, **kwargs)
            self.reload()
        finally:
            # Show triggers output
            if connection.connection:
                for notice in connection.connection.notices[before:]:
                    logger.debug(notice)

    def serialize(self):
        return TopologyHelper.serialize(self)

    @classmethod
    def deserialize(cls, serialized):
        return TopologyHelper.deserialize(serialized)


class PathAggregationManager(models.GeoManager):
    def get_queryset(self):
        self.get_query_set().order_by('order')


class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False, db_column='troncon',
                             verbose_name=_(u"Path"),
                             related_name="aggregations",
                             on_delete=models.DO_NOTHING)  # The CASCADE behavior is enforced at DB-level (see file ../sql/20_evenements_troncons.sql)
    topo_object = models.ForeignKey(Topology, null=False, related_name="aggregations",
                                    db_column='evenement', verbose_name=_(u"Topology"))
    start_position = models.FloatField(db_column='pk_debut', verbose_name=_(u"Start position"))
    end_position = models.FloatField(db_column='pk_fin', verbose_name=_(u"End position"))
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

    class Meta:
        db_table = 'e_r_evenement_troncon'
        verbose_name = _(u"Path aggregation")
        verbose_name_plural = _(u"Path aggregations")
        # Important - represent the order of the path in the Topology path list
        ordering = ['id', ]


class Datasource(StructureRelated):

    source = models.CharField(verbose_name=_(u"Source"), max_length=50)

    class Meta:
        db_table = 'l_b_source'
        verbose_name = _(u"Datasource")
        verbose_name_plural = _(u"Datasources")
        ordering = ['source']

    def __unicode__(self):
        return self.source


@functools.total_ordering
class Stake(StructureRelated):

    stake = models.CharField(verbose_name=_(u"Stake"), max_length=50, db_column='enjeu')

    class Meta:
        db_table = 'l_b_enjeu'
        verbose_name = _(u"Stake")
        verbose_name_plural = _(u"Stakes")
        ordering = ['stake']

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


class Trail(MapEntityMixin, StructureRelated):

    name = models.CharField(verbose_name=_(u"Name"), max_length=64, db_column='nom')
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=64, db_column='depart')
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=64, db_column='arrivee')
    comments = models.TextField(default="", blank=True, verbose_name=_(u"Comments"), db_column='commentaire')

    class Meta:
        db_table = 'l_t_sentier'
        verbose_name = _(u"Trails")
        verbose_name_plural = _(u"Trails")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def geom(self):
        geom = None
        for p in self.paths.all():
            if geom is None:
                geom = LineString(p.geom.coords, srid=settings.SRID)
            else:
                geom = geom.union(p.geom)
        return geom

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self)
