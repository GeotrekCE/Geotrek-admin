import factory
import random
import math

from django.contrib.gis.geos import Point, LineString, Polygon
from django.conf import settings

from caminae.authent.factories import StructureRelatedDefaultFactory
from caminae.common.utils import dbnow
from . import models


class DatasourceFactory(factory.Factory):
    FACTORY_FOR = models.Datasource

    source = factory.Sequence(lambda n: u"Datasource %s" % n)


class StakeFactory(factory.Factory):
    FACTORY_FOR = models.Stake

    stake = factory.Sequence(lambda n: u"Stake %s" % n)


class UsageFactory(factory.Factory):
    FACTORY_FOR = models.Usage

    usage = factory.Sequence(lambda n: u"Usage %s" % n)


class NetworkFactory(factory.Factory):
    FACTORY_FOR = models.Network

    network = factory.Sequence(lambda n: u"Network %s" % n)


class TrailFactory(factory.Factory):
    FACTORY_FOR = models.Trail

    name =  factory.Sequence(lambda n: u"Name %s" % n)
    departure =  factory.Sequence(lambda n: u"Departure %s" % n)
    arrival =  factory.Sequence(lambda n: u"Arrival %s" % n)
    comments =  factory.Sequence(lambda n: u"Comments %s" % n)


class PathFactory(StructureRelatedDefaultFactory):
    FACTORY_FOR = models.Path

    geom = LineString(Point(1, 1, 0), Point(2, 2, 0), srid=settings.SRID)
    geom_cadastre = LineString(Point(5, 5, 0), Point(6, 6, 0), srid=settings.SRID)
    valid = True
    name = factory.Sequence(lambda n: u"name %s" % n)
    departure = factory.Sequence(lambda n: u"departure %s" % n)
    arrival = factory.Sequence(lambda n: u"arrival %s" % n)
    comments = factory.Sequence(lambda n: u"comment %s" % n)

    # Trigger will override :
    date_insert = dbnow()
    date_update = dbnow()
    length = 0.0
    ascent = 0
    descent = 0
    min_elevation = 0
    max_elevation = 0

    # FK that could also be null
    trail = factory.SubFactory(TrailFactory)
    datasource = factory.SubFactory(DatasourceFactory)
    stake = factory.SubFactory(StakeFactory)


def getRandomLineStringInBounds(*args, **kwargs):
    """Return an horizontal line with 2 in bounds random points"""

    srid = settings.SRID
    minx, miny, maxx, maxy = kwargs.pop('bbox', settings.SPATIAL_EXTENT)

    assert srid == 2154, "Following code will use math fns that depends on this srid (floor)"

    # SRID 2154 use integer values. Substract 1 to maxx and maxy to be sure to be in bounds
    get_in_bound_x = lambda: math.floor( random.random() * ((maxx - minx) + 1) + minx )
    get_in_bound_y = lambda: math.floor( random.random() * ((maxy - miny) + 1) + miny )

    p1_x, p2_x = get_in_bound_x(), get_in_bound_x()
    p1_y = p2_y = get_in_bound_y() # make a straight line to be easily identified

    return LineString([Point(p1_x, p1_y, 0), Point(p2_x, p2_y, 0)], srid=srid)


def getExistingLineStringInBounds(*args, **kwargs):
    """Return the geom of the first Path whose geom is in bounds"""
    bbox = kwargs.pop('bbox', settings.SPATIAL_EXTENT)
    p = Polygon.from_bbox(bbox)
    return models.Path.objects.filter(geom__contained=p)[0].geom


## Those two factories return Path whose geom is in bounds
## (better for testing UI for example that always has a bbox filter)
## TODO: Well genereting "in bounds" geom should be the default ?!

class PathInBoundsRandomGeomFactory(PathFactory):
    geom = factory.Sequence(getRandomLineStringInBounds)


class PathInBoundsExistingGeomFactory(PathFactory):
    geom = factory.Sequence(getExistingLineStringInBounds)


class TopologyMixinFactory(factory.Factory):
    FACTORY_FOR = models.TopologyMixin

    # Factory
    # troncons (M2M)
    offset = 0
    deleted = False

    # Trigger will override :
    date_insert = dbnow()
    date_update = dbnow()

    @classmethod
    def create_pathaggregation_from_topo(self, topo_mixin):
        return PathAggregationFactory.create(topo_object=topo_mixin)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
        A topology mixin should be linked to at least one Path (through
        PathAggregation).
        """

        no_path = kwargs.pop('no_path', False)
        topo_mixin = super(TopologyMixinFactory, cls)._prepare(create, **kwargs)

        if not no_path and create:
            cls.create_pathaggregation_from_topo(topo_mixin)
            # Note that it is not possible to attach a related object before the
            # topo_mixin has an ID.
        return topo_mixin


class TopologyMixinInBoundsRandomGeomFactory(TopologyMixinFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return PathAggregationInBoundsRandomGeomFactory.create(topo_object=topo_mixin)


class TopologyMixinInBoundsExistingGeomFactory(TopologyMixinFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return PathAggregationInBoundsExistingGeomFactory.create(topo_object=topo_mixin)


class PathAggregationFactory(factory.Factory):
    FACTORY_FOR = models.PathAggregation

    path = factory.SubFactory(PathFactory)
    topo_object = factory.SubFactory(TopologyMixinFactory)

    start_position = 0.0
    end_position = 1.0


class PathAggregationInBoundsRandomGeomFactory(PathAggregationFactory):
    path = factory.SubFactory(PathInBoundsRandomGeomFactory)


class PathAggregationInBoundsExistingGeomFactory(PathAggregationFactory):
    path = factory.SubFactory(PathInBoundsExistingGeomFactory)
