# -*- coding: utf-8 -*-

import factory
import random
import math

from django.contrib.gis.geos import Point, LineString, Polygon
from django.conf import settings

from geotrek.authent.factories import StructureRelatedDefaultFactory
from geotrek.common.utils import dbnow
from . import models


class PathSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PathSource

    source = factory.Sequence(lambda n: u"PathSource %s" % n)


class StakeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Stake

    stake = factory.Sequence(lambda n: u"Stake %s" % n)


class UsageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Usage

    usage = factory.Sequence(lambda n: u"Usage %s" % n)


class NetworkFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Network

    network = factory.Sequence(lambda n: u"Network %s" % n)


class ComfortFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Comfort

    comfort = factory.Sequence(lambda n: u"Comfort %s" % n)


class PathFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.Path

    # (700000, 6600000) = Lambert93 origin (3.0° E, 46.5° N)
    geom = LineString(Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID)
    geom_cadastre = LineString(Point(5, 5), Point(6, 6), srid=settings.SRID)
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
    comfort = factory.SubFactory(ComfortFactory)
    source = factory.SubFactory(PathSourceFactory)
    stake = factory.SubFactory(StakeFactory)


def getRandomLineStringInBounds(*args, **kwargs):
    """Return an horizontal line with 2 in bounds random points"""

    srid = settings.SRID
    minx, miny, maxx, maxy = kwargs.pop('bbox', settings.SPATIAL_EXTENT)

    assert srid == 2154, "Following code will use math fns that depends on this srid (floor)"

    # SRID 2154 use integer values. Substract 1 to maxx and maxy to be sure to be in bounds
    def get_in_bound_x():
        return math.floor(random.random() * ((maxx - minx) + 1) + minx)

    def get_in_bound_y():
        return math.floor(random.random() * ((maxy - miny) + 1) + miny)

    p1_x, p2_x = get_in_bound_x(), get_in_bound_x()
    p1_y = p2_y = get_in_bound_y()  # make a straight line to be easily identified

    return LineString([Point(p1_x, p1_y), Point(p2_x, p2_y)], srid=srid)


def getExistingLineStringInBounds(*args, **kwargs):
    """Return the geom of the first Path whose geom is in bounds"""
    bbox = kwargs.pop('bbox', settings.SPATIAL_EXTENT)
    p = Polygon.from_bbox(bbox)
    return models.Path.objects.filter(geom__contained=p)[0].geom


# Those two factories return Path whose geom is in bounds
# (better for testing UI for example that always has a bbox filter)
# TODO: Well genereting "in bounds" geom should be the default ?!

class PathInBoundsRandomGeomFactory(PathFactory):
    geom = factory.Sequence(getRandomLineStringInBounds)


class PathInBoundsExistingGeomFactory(PathFactory):
    geom = factory.Sequence(getExistingLineStringInBounds)


class TopologyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Topology

    # Factory
    # troncons (M2M)
    offset = 0
    deleted = False

    # Trigger will override :
    date_insert = dbnow()
    date_update = dbnow()

    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return PathAggregationFactory.create(topo_object=topo_mixin)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
        A topology mixin should be linked to at least one Path (through
        PathAggregation).
        """
        no_path = kwargs.pop('no_path', False)
        topo_mixin = super(TopologyFactory, cls)._prepare(create, **kwargs)

        if not no_path and create:
            cls.create_pathaggregation_from_topo(topo_mixin)
            # Note that it is not possible to attach a related object before the
            # topo_mixin has an ID.
        return topo_mixin


class PointTopologyFactory(TopologyFactory):
    @classmethod
    def create_pathaggregation_from_topo(cls, topo_mixin):
        return PathAggregationFactory.create(topo_object=topo_mixin,
                                             start_position=0.0,
                                             end_position=0.0)


class PathAggregationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PathAggregation

    path = factory.SubFactory(PathFactory)
    topo_object = factory.SubFactory(TopologyFactory)

    start_position = 0.0
    end_position = 1.0
    order = 0


class TrailFactory(TopologyFactory):
    class Meta:
        model = models.Trail

    name = factory.Sequence(lambda n: u"Name %s" % n)
    departure = factory.Sequence(lambda n: u"Departure %s" % n)
    arrival = factory.Sequence(lambda n: u"Arrival %s" % n)
    comments = factory.Sequence(lambda n: u"Comments %s" % n)
