import logging
import functools

import simplekml
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.geos import fromstr, LineString

from mapentity.models import MapEntityMixin
from mapentity.serializers import plain_text

from geotrek.authent.models import StructureRelated, StructureOrNoneRelated
from geotrek.common.mixins import (TimeStampedModelMixin, NoDeleteMixin,
                                   AddPropertyMixin)
from geotrek.common.utils import classproperty
from geotrek.common.utils.postgresql import debug_pg_notices
from geotrek.altimetry.models import AltimetryMixin

from .helpers import PathHelper, TopologyHelper
from django.db import connections, DEFAULT_DB_ALIAS

from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)


def simplify_coords(coords):
    if isinstance(coords, (list, tuple)):
        return [simplify_coords(coord) for coord in coords]
    elif isinstance(coords, float):
        return round(coords, 7)
    raise Exception("Param is {}. Should be <list>, <tuple> or <float>".format(type(coords)))


class PathManager(models.Manager):
    # Use this manager when walking through FK/M2M relationships
    use_for_related_fields = True

    def get_queryset(self):
        """Hide all ``Path`` records that are not marked as visible.
        """
        return super(PathManager, self).get_queryset().filter(visible=True)


class PathInvisibleManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return super(PathInvisibleManager, self).get_queryset()

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).


class Path(AddPropertyMixin, MapEntityMixin, AltimetryMixin,
           TimeStampedModelMixin, StructureRelated):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=True)
    geom_cadastre = models.LineStringField(null=True, srid=settings.SRID, spatial_index=True,
                                           editable=False)
    valid = models.BooleanField(default=True, verbose_name=_("Validity"),
                                help_text=_("Approved by manager"))
    visible = models.BooleanField(default=True, verbose_name=_("Visible"),
                                  help_text=_("Shown in lists and maps"))
    name = models.CharField(null=True, blank=True, max_length=250, verbose_name=_("Name"),
                            help_text=_("Official name"))
    comments = models.TextField(null=True, blank=True, verbose_name=_("Comments"),
                                help_text=_("Remarks"))

    departure = models.CharField(null=True, blank=True, default="", max_length=250, verbose_name=_("Departure"),
                                 help_text=_("Departure place"))
    arrival = models.CharField(null=True, blank=True, default="", max_length=250, verbose_name=_("Arrival"),
                               help_text=_("Arrival place"))

    comfort = models.ForeignKey('Comfort', on_delete=models.CASCADE,
                                null=True, blank=True, related_name='paths',
                                verbose_name=_("Comfort"))
    source = models.ForeignKey('PathSource', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='paths',
                               verbose_name=_("Source"))
    stake = models.ForeignKey('Stake', on_delete=models.CASCADE,
                              null=True, blank=True, related_name='paths',
                              verbose_name=_("Maintenance stake"))
    usages = models.ManyToManyField('Usage',
                                    blank=True, related_name="paths",
                                    verbose_name=_("Usages"))
    networks = models.ManyToManyField('Network',
                                      blank=True, related_name="paths",
                                      verbose_name=_("Networks"))
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    draft = models.BooleanField(default=False, verbose_name=_("Draft"), db_index=True)

    objects = PathManager()
    include_invisible = PathInvisibleManager()

    is_reversed = False

    @property
    def length_2d(self):
        if self.geom:
            return self.geom.length
        else:
            return None

    @classproperty
    def length_2d_verbose_name(cls):
        return _("2D Length")

    @property
    def length_2d_display(self):
        return round(self.length_2d, 1)

    def kml(self):
        """ Exports path into KML format, add geometry as linestring """
        kml = simplekml.Kml()
        geom3d = self.geom_3d.transform(4326, clone=True)  # KML uses WGS84

        line = kml.newlinestring(name=self.name,
                                 description=plain_text(self.comments),
                                 coords=simplify_coords(geom3d.coords))
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        return kml.kml()

    def __str__(self):
        return self.name or _('path %d') % self.pk

    class Meta:
        verbose_name = _("Path")
        verbose_name_plural = _("Paths")
        permissions = MapEntityMixin._meta.permissions + [("add_draft_path", "Can add draft Path"),
                                                          ("change_draft_path", "Can change draft Path"),
                                                          ("delete_draft_path", "Can delete draft Path"),
                                                          ]

    @classmethod
    def closest(cls, point, exclude=None):
        """
        Returns the closest path of the point.
        Will fail if no path in database.
        """
        # TODO: move to custom manager
        if point.srid != settings.SRID:
            point = point.transform(settings.SRID, clone=True)
        qs = cls.objects.exclude(draft=True)
        if exclude:
            qs = qs.exclude(pk=exclude.pk)
        return qs.exclude(visible=False).annotate(distance=Distance('geom', point)).order_by('distance')[0]

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

    def reload(self):
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

    def delete(self, *args, **kwargs):
        if not settings.TREKKING_TOPOLOGY_ENABLED:
            return super(Path, self).delete(*args, **kwargs)
        topologies = list(self.topology_set.filter())
        r = super(Path, self).delete(*args, **kwargs)
        if not Path.objects.exists():
            return r
        for topology in topologies:
            if isinstance(topology.geom, Point):
                closest = self.closest(topology.geom, self)
                position, offset = closest.interpolate(topology.geom)
                new_topology = Topology.objects.create()
                aggrobj = PathAggregation(topo_object=new_topology,
                                          start_position=position,
                                          end_position=position,
                                          path=closest)
                aggrobj.save()
                point = Point(topology.geom.x, topology.geom.y, srid=settings.SRID)
                new_topology.geom = point
                new_topology.offset = offset
                new_topology.position = position
                new_topology.save()
                topology.mutate(new_topology)
        return r

    @property
    def name_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self,
                                                                 self)

    @property
    def name_csv_display(self):
        return str(self)

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
            return ", ".join([str(t) for t in trails])
        return _("None")

    @property
    def usages_display(self):
        return ", ".join([str(u) for u in self.usages.all()])

    @property
    def networks_display(self):
        return ", ".join([str(n) for n in self.networks.all()])

    @classmethod
    def get_create_label(cls):
        return _("Add a new path")

    @property
    def checkbox(self):
        return '<input type="checkbox" name="{}[]" value="{}" />'.format('path',
                                                                         self.pk)

    @classproperty
    def checkbox_verbose_name(cls):
        return _("Action")

    @property
    def checkbox_display(self):
        return self.checkbox

    def topologies_by_path(self, default_dict):
        if 'geotrek.core' in settings.INSTALLED_APPS:
            for trail in self.trails:
                default_dict[_('Trails')].append({'name': trail.name, 'url': trail.get_detail_url()})
        if 'geotrek.trekking' in settings.INSTALLED_APPS:
            for trek in self.treks:
                default_dict[_('Treks')].append({'name': trek.name, 'url': trek.get_detail_url()})
            for service in self.services:
                default_dict[_('Services')].append(
                    {'name': service.type.name, 'url': service.get_detail_url()})
            for poi in self.pois:
                default_dict[_('Pois')].append({'name': poi.name, 'url': poi.get_detail_url()})
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            for signage in self.signages:
                default_dict[_('Signages')].append({'name': signage.name, 'url': signage.get_detail_url()})
        if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
            for infrastructure in self.infrastructures:
                default_dict[_('Infrastructures')].append(
                    {'name': infrastructure.name, 'url': infrastructure.get_detail_url()})
        if 'geotrek.maintenance' in settings.INSTALLED_APPS:
            for intervention in self.interventions:
                default_dict[_('Interventions')].append(
                    {'name': intervention.name, 'url': intervention.get_detail_url()})

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

    @property
    def extent(self):
        return self.geom.transform(settings.API_SRID, clone=True).extent if self.geom else None

    def distance(self, to_cls):
        """Distance to associate this path to another class"""
        return None


class Topology(AddPropertyMixin, AltimetryMixin, TimeStampedModelMixin, NoDeleteMixin):
    paths = models.ManyToManyField(Path, through='PathAggregation', verbose_name=_("Path"))
    offset = models.FloatField(default=0.0, verbose_name=_("Offset"))  # in SRID units
    kind = models.CharField(editable=False, verbose_name=_("Kind"), max_length=32)
    geom_need_update = models.BooleanField(default=False)

    geom = models.GeometryField(editable=(not settings.TREKKING_TOPOLOGY_ENABLED),
                                srid=settings.SRID, null=True,
                                default=None, spatial_index=True)

    """ Fake srid attribute, that prevents transform() calls when using Django map widgets. """
    srid = settings.API_SRID

    class Meta:
        verbose_name = _("Topology")
        verbose_name_plural = _("Topologies")

    def __init__(self, *args, **kwargs):
        super(Topology, self).__init__(*args, **kwargs)
        if not self.pk and not self.kind:
            self.kind = self.__class__.KIND

    @property
    def length_2d(self):
        if self.geom and not self.ispoint():
            return round(self.geom.length, 1)

        else:
            return None

    @classproperty
    def length_2d_verbose_name(cls):
        return _("2D Length")

    @property
    def length_2d_display(self):
        return self.length_2d

    @classproperty
    def KIND(cls):
        return cls._meta.object_name.upper()

    def __str__(self):
        return "%s (%s)" % (_("Topology"), self.pk)

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
        # and NULL in geom (see update_geometry_of_topology:: IF t_count = 0)
        self.deleted = False
        self.geom = other.geom
        self.save(update_fields=['deleted', 'geom'])

        # Now copy all agregations from other to self
        aggrs = other.aggregations.all()
        # A point has only one aggregation, except if it is on an intersection.
        # In this case, the trigger will create them, so ignore them here.
        if other.ispoint():
            aggrs = aggrs[:1]
        PathAggregation.objects.bulk_create([
            PathAggregation(
                path=aggr.path,
                topo_object=self,
                start_position=aggr.start_position,
                end_position=aggr.end_position,
                order=aggr.order
            )
            for aggr in aggrs
        ])
        self.reload()
        if delete:
            other.delete(force=True)  # Really delete it from database
        return self

    def reload(self):
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


class PathAggregationManager(models.Manager):
    def get_queryset(self):
        return super(PathAggregationManager, self).get_queryset().order_by('order')


class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False,
                             verbose_name=_("Path"),
                             related_name="aggregations",
                             on_delete=models.DO_NOTHING)  # The CASCADE behavior is enforced at DB-level (see file ../sql/30_topologies_paths.sql)
    topo_object = models.ForeignKey(Topology, null=False, related_name="aggregations", on_delete=models.CASCADE,
                                    verbose_name=_("Topology"))
    start_position = models.FloatField(verbose_name=_("Start position"), db_index=True)
    end_position = models.FloatField(verbose_name=_("End position"), db_index=True)
    order = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Order"))

    # Override default manager
    objects = PathAggregationManager()

    def __str__(self):
        return "%s (%s-%s: %s - %s)" % (_("Path aggregation"), self.path.pk, self.path.name, self.start_position, self.end_position)

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
        return (self.start_position == 0.0 and self.end_position == 1.0
                or self.start_position == 1.0 and self.end_position == 0.0)

    @debug_pg_notices
    def save(self, *args, **kwargs):
        return super(PathAggregation, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Path aggregation")
        verbose_name_plural = _("Path aggregations")
        # Important - represent the order of the path in the Topology path list
        ordering = ['order', ]


class PathSource(StructureOrNoneRelated):

    source = models.CharField(verbose_name=_("Source"), max_length=50)

    class Meta:
        verbose_name = _("Path source")
        verbose_name_plural = _("Path sources")
        ordering = ['source']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.source, self.structure.name)
        return self.source


@functools.total_ordering
class Stake(StructureOrNoneRelated):

    stake = models.CharField(verbose_name=_("Stake"), max_length=50)

    class Meta:
        verbose_name = _("Maintenance stake")
        verbose_name_plural = _("Maintenance stakes")
        ordering = ['id']

    def __lt__(self, other):
        if other is None:
            return False
        return self.pk < other.pk

    def __eq__(self, other):
        return isinstance(other, Stake) \
            and self.pk == other.pk

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.stake, self.structure.name)
        return self.stake


class Comfort(StructureOrNoneRelated):

    comfort = models.CharField(verbose_name=_("Comfort"), max_length=50)

    class Meta:
        verbose_name = _("Comfort")
        verbose_name_plural = _("Comforts")
        ordering = ['comfort']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.comfort, self.structure.name)
        return self.comfort


class Usage(StructureOrNoneRelated):

    usage = models.CharField(verbose_name=_("Usage"), max_length=50)

    class Meta:
        verbose_name = _("Usage")
        verbose_name_plural = _("Usages")
        ordering = ['usage']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.usage, self.structure.name)
        return self.usage


class Network(StructureOrNoneRelated):

    network = models.CharField(verbose_name=_("Network"), max_length=50)

    class Meta:
        verbose_name = _("Network")
        verbose_name_plural = _("Networks")
        ordering = ['network']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.network, self.structure.name)
        return self.network


class Trail(MapEntityMixin, Topology, StructureRelated):
    topo_object = models.OneToOneField(Topology, parent_link=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    departure = models.CharField(verbose_name=_("Departure"), blank=True, max_length=64)
    arrival = models.CharField(verbose_name=_("Arrival"), blank=True, max_length=64)
    comments = models.TextField(default="", blank=True, verbose_name=_("Comments"))
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = _("Trail")
        verbose_name_plural = _("Trails")
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def name_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self,
                                                                 self)

    @classmethod
    def path_trails(cls, path):
        trails = cls.objects.existing().filter(aggregations__path=path)
        # The following part prevents conflict with default trail ordering
        # ProgrammingError: SELECT DISTINCT ON expressions must match initial ORDER BY expressions
        return trails.order_by('topo_object').distinct('topo_object')

    def kml(self):
        """ Exports path into KML format, add geometry as linestring """
        kml = simplekml.Kml()
        geom3d = self.geom_3d.transform(4326, clone=True)  # KML uses WGS84
        line = kml.newlinestring(name=self.name,
                                 description=plain_text(self.comments),
                                 coords=simplify_coords(geom3d.coords))
        line.style.linestyle.color = simplekml.Color.red  # Red
        line.style.linestyle.width = 4  # pixels
        return kml.kml()


Path.add_property('trails', lambda self: Trail.path_trails(self), _("Trails"))
Topology.add_property('trails', lambda self: Trail.overlapping(self), _("Trails"))
