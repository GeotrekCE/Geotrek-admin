# -*- coding: utf-8 -*-

import logging
import collections

from django.contrib.gis.db import models
from django.db import connection
from django.db.models import Manager as DefaultManager
from django.utils import simplejson
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import LineString, Point

from caminae.authent.models import StructureRelated
from caminae.common.utils import elevation_profile, classproperty
from caminae.mapentity.models import MapEntityMixin


logger = logging.getLogger(__name__)

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).

class Path(MapEntityMixin, StructureRelated):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=False,
                                  dim=3)
    geom_cadastre = models.LineStringField(null=True, srid=settings.SRID,
                                           spatial_index=False, dim=3)
    valid = models.BooleanField(db_column='troncon_valide', default=True, verbose_name=_(u"Validity"))
    name = models.CharField(null=True, blank=True, max_length=20, db_column='nom_troncon', verbose_name=_(u"Name"))
    comments = models.TextField(null=True, blank=True, db_column='remarques', verbose_name=_(u"Comments"))

    departure = models.CharField(blank=True, default="", max_length=250, db_column='depart', verbose_name=_(u"Departure"))
    arrival = models.CharField(blank=True, default="", max_length=250, db_column='arrivee', verbose_name=_(u"Arrival"))
    
    comfort =  models.ForeignKey('Comfort',
                                 null=True, blank=True, related_name='paths',
                                 verbose_name=_("Comfort"))
    # Override default manager
    objects = models.GeoManager()

    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(editable=False, verbose_name=_(u"Insertion date"))
    date_update = models.DateTimeField(editable=False, verbose_name=_(u"Update date"))
    length = models.FloatField(editable=False, default=0, db_column='longueur', verbose_name=_(u"Length"))
    ascent = models.IntegerField(
            editable=False, default=0, db_column='denivelee_positive', verbose_name=_(u"Ascent"))
    descent = models.IntegerField(
            editable=False, default=0, db_column='denivelee_negative', verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(
            editable=False, default=0, db_column='altitude_minimum', verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(
            editable=False, default=0, db_column='altitude_maximum', verbose_name=_(u"Maximum elevation"))


    trail = models.ForeignKey('Trail',
            null=True, blank=True, related_name='paths',
            verbose_name=_("Trail"))
    datasource = models.ForeignKey('Datasource',
            null=True, blank=True, related_name='paths',
            verbose_name=_("Datasource"))
    stake = models.ForeignKey('Stake',
            null=True, blank=True, related_name='paths',
            verbose_name=_("Stake"))
    usages = models.ManyToManyField('Usage',
            blank=True, null=True, related_name="paths",
            verbose_name=_(u"Usages"))
    networks = models.ManyToManyField('Network',
            blank=True, null=True, related_name="paths",
            verbose_name=_(u"Networks"))

    def __unicode__(self):
        return self.name or 'path %d' % self.pk

    class Meta:
        db_table = 'troncons'
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

    def interpolate(self, point):
        """
        Returns position ([0.0-1.0]) and offset (distance) of the point
        along this path.
        """
        if not self.pk:
            raise ValueError("Cannot compute interpolation on unsaved path")
        if point.srid != settings.SRID:
            point.transform(settings.SRID)
        cursor = connection.cursor()
        sql = """
        SELECT position, distance
        FROM ft_troncon_interpolate(%(pk)s, ST_GeomFromText('POINT(%(x)s %(y)s %(z)s)',%(srid)s))
             AS (position FLOAT, distance FLOAT)
        """ % {'pk': self.pk,
               'x': point.x,
               'y': point.y,
               'z': 0,  # TODO: does it matter ?
               'srid': settings.SRID}
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0]

    def reload(self):
        # Update object's computed values (reload from database)
        tmp = self.__class__.objects.get(pk=self.pk)
        self.date_insert = tmp.date_insert
        self.date_update = tmp.date_update
        self.length = tmp.length
        self.ascent = tmp.ascent
        self.descent = tmp.descent
        self.min_elevation = tmp.min_elevation
        self.max_elevation = tmp.max_elevation
        self.geom = tmp.geom

    def save(self, *args, **kwargs):
        before = len(connection.connection.notices) if connection.connection else 0
        try:
            super(Path, self).save(*args, **kwargs)
            self.reload()
        finally:
            # Show triggers output
            if connection.connection:
                for notice in connection.connection.notices[before:]:
                    logger.debug(notice)

    def get_elevation_profile(self):
        """
        Extract elevation profile from path.
        """
        return elevation_profile(self.geom)

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


class NoDeleteMixin(models.Model):
    deleted = models.BooleanField(editable=False, default=False, db_column='supprime', verbose_name=_(u"Deleted"))

    def delete(self, using=None):
        self.deleted = True
        self.save(using=using)

    class Meta:
        abstract = True

    @classmethod
    def get_manager_cls(cls, parent_mgr_cls=DefaultManager):

        class NoDeleteManager(parent_mgr_cls):
            # Use this manager when walking through FK/M2M relationships
            use_for_related_fields = True

            # Filter out deleted objects
            def existing(self):
                return self.get_query_set().filter(deleted=False)

        return NoDeleteManager


class Topology(NoDeleteMixin):
    paths = models.ManyToManyField(Path, editable=False, db_column='troncons', through='PathAggregation', verbose_name=_(u"Path"))
    offset = models.FloatField(default=0.0, db_column='decallage', verbose_name=_(u"Offset"))  # in SRID units
    kind = models.CharField(editable=False, verbose_name=_(u"Kind"), max_length=32)

    # Override default manager
    objects = NoDeleteMixin.get_manager_cls(models.GeoManager)()

    # Computed values (managed at DB-level with triggers)
    date_insert = models.DateTimeField(editable=False, verbose_name=_(u"Insertion date"))
    date_update = models.DateTimeField(editable=False, verbose_name=_(u"Update date"))
    length = models.FloatField(default=0.0, editable=False, db_column='longueur', verbose_name=_(u"Length"))
    geom = models.GeometryField(editable=False, srid=settings.SRID, null=True,
                                blank=True, spatial_index=False, dim=3)

    class Meta:
        db_table = 'evenements'
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

    @classmethod
    def overlapping(self, edges):
        """ Return a list of Topology objects if specified edges overlap them.
        TODO: So far, the algorithm is quite simple, and not precise. Indeed
        it returns edges that "share" the same paths, and not exactly overlapping.
        """
        paths = []
        for edge in edges:
            paths.extend(edge.topo_object.paths.select_related(depth=1).all())
        topos = []
        for path in set(paths):
            topos += [aggr.topo_object for aggr in path.aggregations.select_related(depth=1).all()]
        return topos

    def __unicode__(self):
        return u"%s (%s)" % (_(u"Topology"), self.pk)

    def ispoint(self):
        for aggr in self.aggregations.all():
            if aggr.start_position == aggr.end_position:
                return True
            break
        return False

    def add_path(self, path, start=0.0, end=1.0):
        """
        Shortcut function to add paths into this topology.
        """
        from .factories import PathAggregationFactory
        aggr = PathAggregationFactory.create(topo_object=self, 
                                             path=path, 
                                             start_position=start, 
                                             end_position=end)
        # Since a trigger modifies geom, we reload the object
        self.reload()
        return aggr

    def mutate(self, other, delete=True):
        """
        Take alls attributes of the other topology specified and
        save them into this one. Optionnally deletes the other.
        """
        self.offset = other.offset
        self.save()
        PathAggregation.objects.filter(topo_object=self).delete()
        aggrs = other.aggregations.all()
        # A point has only one aggregation, except if it is on an intersection.
        # In this case, the trigger will create them, so ignore them here.
        if other.ispoint():
            aggrs = aggrs[:1]
        for aggr in aggrs:
            self.add_path(aggr.path, aggr.start_position, aggr.end_position)
        if delete:
            other.delete()
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
            self.offset = tmp.offset # /!\ offset may be set by a trigger OR in
                                     # the django code, reload() will override
                                     # any unsaved value
            self.geom = tmp.geom
        return self

    def save(self, *args, **kwargs):
        # HACK: these fields are readonly from the Django point of view
        # but they can be changed at DB level. Since Django write all fields
        # to DB anyway, it is important to update it before writting
        if self.pk:
            tmp = self.__class__.objects.get(pk=self.pk)
            self.length = tmp.length
            self.geom = tmp.geom

        if not self.kind:
            if self.KIND == "TOPOLOGYMIXIN":
                raise Exception("Cannot save abstract topologies")
            self.kind = self.__class__.KIND

        super(Topology, self).save(*args, **kwargs)
        self.reload()

    @classmethod
    def deserialize(cls, serialized):
        from .factories import TopologyFactory
        objdict = serialized
        if isinstance(serialized, basestring):
            try:
                objdict = simplejson.loads(serialized)
            except simplejson.JSONDecodeError, e:
                raise ValueError(_("Invalid serialization: %s") % e)
        kind = objdict.get('kind')
        lat = objdict.get('lat')
        lng = objdict.get('lng')
        # Point topology ?
        if lat and lng:
            return cls._topologypoint(lng, lat, kind)

        # Path aggregation
        topology = TopologyFactory.create(no_path=True, kind=kind, offset=objdict.get('offset', 0.0))
        PathAggregation.objects.filter(topo_object=topology).delete()

        # Start repopulating from serialized data
        positions = objdict.get('positions', {})
        paths = objdict['paths']
        # Check that paths should be unique
        if len(set(paths)) != len(paths):
            paths = collections.Counter(paths)
            extras = [p for p in paths if paths[p]>1]
            raise ValueError(_("Paths are not unique : %s") % extras)

        # Create path aggregations
        for i, path in enumerate(paths):
            try:
                path = Path.objects.get(pk=path)
            except Path.DoesNotExist, e:
                raise ValueError(str(e))
            # Javascript hash keys are parsed as a string
            # Provides default values
            start_position, end_position = positions.get(str(i), (False, False))
            if start_position != end_position \
               and i > 0 and i < len(paths) -1:
                raise ValueError(_("Invalid serialization of intermediate markers"))

            aggrobj = PathAggregation(topo_object=topology,
                                      start_position=start_position or 0.0,
                                      end_position=end_position or 1.0,
                                      path=path)
            aggrobj.save()
        return topology

    @classmethod
    def _topologypoint(cls, lng, lat, kind=None):
        """
        Receives a point (lng, lat) with API_SRID, and returns
        a topology objects with a computed path aggregation.
        """
        from .factories import TopologyFactory
        # Find closest path
        point = Point((lng, lat), srid=settings.API_SRID)
        point.transform(settings.SRID)
        closest = Path.closest(point)
        position, offset = closest.interpolate(point)
        # We can now instantiante a Topology object
        topology = TopologyFactory.create(no_path=True, kind=kind, offset=offset)
        aggrobj = PathAggregation(topo_object=topology,
                                  start_position=position,
                                  end_position=position,
                                  path=closest)
        aggrobj.save()
        return topology

    def geom_as_point(self):
        geom = self.geom
        if geom.geom_type != 'Point':
            logger.warning("Topology has wrong geometry type : %s instead of Point" % geom.geom_type)
            geom = Point(geom.coords[0], srid=settings.SRID)
        return geom

    def serialize(self):
        # Point topology
        if self.ispoint():
            geom = self.geom_as_point()
            point = geom.transform(settings.API_SRID, clone=True)
            objdict = dict(kind=self.kind, lng=point.x, lat=point.y)
        else:
            # Line topology
            # Fetch properly ordered aggregations
            aggregations = self.aggregations.all()
            paths = list(aggregations.values_list('path__pk', flat=True))
            # We may filter out aggregations that have default values (0.0 and 1.0)...
            positions = dict(
                (i, (a.start_position, a.end_position))
                for i, a in enumerate(aggregations)
                if (a.start_position, a.end_position) != (0, 1)
            )

            objdict = dict(kind=self.kind,
                           offset=self.offset,
                           positions=positions,
                           paths=paths,
                           )
        return simplejson.dumps(objdict)


class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False, db_column='troncon',
                             verbose_name=_(u"Path"),
                             related_name="aggregations",
                             on_delete=models.DO_NOTHING) # The CASCADE behavior is enforced at DB-level (see file ../sql/20_evenements_troncons.sql)
    topo_object = models.ForeignKey(Topology, null=False, related_name="aggregations",
                                    db_column='evenement', verbose_name=_(u"Topology"))
    start_position = models.FloatField(db_column='pk_debut', verbose_name=_(u"Start position"))
    end_position = models.FloatField(db_column='pk_fin', verbose_name=_(u"End position"))

    # Override default manager
    objects = models.GeoManager()

    def __unicode__(self):
        return u"%s (%s: %s - %s)" % (_("Path aggregation"), self.path.pk, self.start_position, self.end_position)

    class Meta:
        db_table = 'evenements_troncons'
        verbose_name = _(u"Path aggregation")
        verbose_name_plural = _(u"Path aggregations")
        # Important - represent the order of the path in the Topology path list
        ordering = ['id', ]



class Datasource(StructureRelated):

    source = models.CharField(verbose_name=_(u"Source"), max_length=50)

    class Meta:
        db_table = 'source_donnees'
        verbose_name = _(u"Datasource")
        verbose_name_plural = _(u"Datasources")

    def __unicode__(self):
        return self.source


class Stake(StructureRelated):

    stake = models.CharField(verbose_name=_(u"Stake"), max_length=50)

    class Meta:
        db_table = 'enjeu'
        verbose_name = _(u"Stake")
        verbose_name_plural = _(u"Stakes")

    def __lt__(self, other):
        return self.pk < other.pk

    def __unicode__(self):
        return self.stake


class Comfort(StructureRelated):

    comfort = models.CharField(verbose_name=_(u"Comfort"), max_length=50)

    class Meta:
        db_table = 'bib_confort'
        verbose_name = _(u"Comfort")
        verbose_name_plural = _(u"Comforts")

    def __unicode__(self):
        return self.comfort


class Usage(StructureRelated):

    usage = models.CharField(verbose_name=_(u"Usage"), max_length=50)

    class Meta:
        db_table = 'usage'
        verbose_name = _(u"Usage")
        verbose_name_plural = _(u"Usages")

    def __unicode__(self):
        return self.usage


class Network(StructureRelated):

    network = models.CharField(verbose_name=_(u"Network"), max_length=50)

    class Meta:
        db_table = 'reseau_troncon'
        verbose_name = _(u"Network")
        verbose_name_plural = _(u"Networks")

    def __unicode__(self):
        return self.network


class Trail(MapEntityMixin, StructureRelated):

    name = models.CharField(verbose_name=_(u"Name"), max_length=64)
    departure = models.CharField(verbose_name=_(u"Departure"), max_length=64)
    arrival = models.CharField(verbose_name=_(u"Arrival"), max_length=64)
    comments = models.TextField(default="", verbose_name=_(u"Comments"))

    class Meta:
        db_table = 'sentier'
        verbose_name = _(u"Trails")
        verbose_name_plural = _(u"Trails")

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
