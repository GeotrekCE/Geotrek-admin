import math
import random

import factory
from django.conf import settings
from django.contrib.gis.geos import LineString, Point, Polygon

from geotrek.authent.tests.factories import StructureRelatedDefaultFactory
from geotrek.common.utils import dbnow

from .. import models


class PathSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PathSource

    source = factory.Sequence(lambda n: f"PathSource {n}")


class StakeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Stake

    stake = factory.Sequence(lambda n: f"Stake {n}")


class UsageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Usage

    usage = factory.Sequence(lambda n: f"Usage {n}")


class NetworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Network

    network = factory.Sequence(lambda n: f"Network {n}")


class ComfortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Comfort

    comfort = factory.Sequence(lambda n: f"Comfort {n}")


class PathFactory(StructureRelatedDefaultFactory):
    class Meta:
        model = models.Path

    # (700000, 6600000) = Lambert93 origin (3.0° E, 46.5° N)
    geom = LineString(
        Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID
    )
    geom_cadastre = LineString(Point(5, 5), Point(6, 6), srid=settings.SRID)
    valid = True
    name = factory.Sequence(lambda n: f"name {n}")
    comments = factory.Sequence(lambda n: f"comment {n}")

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
    minx, miny, maxx, maxy = kwargs.pop("bbox", settings.SPATIAL_EXTENT)

    assert srid == 2154, (
        "Following code will use math fns that depends on this srid (floor)"
    )

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
    bbox = kwargs.pop("bbox", settings.SPATIAL_EXTENT)
    p = Polygon.from_bbox(bbox)
    return models.Path.objects.filter(geom__contained=p)[0].geom


# Those two factories return Path whose geom is in bounds
# (better for testing UI for example that always has a bbox filter)
# TODO: Well genereting "in bounds" geom should be the default ?!


class PathInBoundsRandomGeomFactory(PathFactory):
    geom = factory.Sequence(getRandomLineStringInBounds)


class PathInBoundsExistingGeomFactory(PathFactory):
    geom = factory.Sequence(getExistingLineStringInBounds)


class TopologyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topology

    # Factory
    # paths (M2M)
    if not settings.TREKKING_TOPOLOGY_ENABLED:
        geom = "SRID=2154;LINESTRING (700000 6600000, 700100 6600100)"
    offset = 0
    deleted = False

    # Trigger will override :
    date_insert = dbnow()
    date_update = dbnow()

    @factory.post_generation
    def paths(obj, create, paths):
        if not create or not settings.TREKKING_TOPOLOGY_ENABLED:
            return
        if paths is None:
            PathAggregationFactory.create(topo_object=obj)
            return
        for i, path in enumerate(paths):
            if isinstance(path, tuple):
                obj.add_path(path[0], path[1], path[2], i)
            else:
                obj.add_path(path, 0, 1, i)


class PointTopologyFactory(TopologyFactory):
    if not settings.TREKKING_TOPOLOGY_ENABLED:
        geom = "SRID=2154;POINT (700000 6600000)"

    @factory.post_generation
    def paths(obj, create, paths):
        if not create or not settings.TREKKING_TOPOLOGY_ENABLED:
            return
        if paths is None:
            PointPathAggregationFactory.create(topo_object=obj)
            return
        path = paths[0]
        if isinstance(path, tuple):
            obj.add_path(path[0], path[1], path[2])
        else:
            obj.add_path(path, 0, 0)


class PathAggregationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PathAggregation

    path = factory.SubFactory(PathFactory)
    topo_object = factory.SubFactory(TopologyFactory)

    start_position = 0.0
    end_position = 1.0
    order = 0


class PointPathAggregationFactory(PathAggregationFactory):
    end_position = 0


class TrailFactory(TopologyFactory):
    class Meta:
        model = models.Trail

    name = factory.Sequence(lambda n: f"Name {n}")
    departure = factory.Sequence(lambda n: f"Departure {n}")
    arrival = factory.Sequence(lambda n: f"Arrival {n}")
    comments = factory.Sequence(lambda n: f"Comments {n}")


class TrailCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TrailCategory

    label = factory.Sequence(lambda n: f"Trail category {n}")


class CertificationLabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CertificationLabel

    label = factory.Sequence(lambda n: f"My certification label {n}")


class CertificationStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CertificationStatus

    label = factory.Sequence(lambda n: f"My certification status {n}")


class CertificationTrailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CertificationTrail

    trail = factory.SubFactory(TrailFactory)
    certification_label = factory.SubFactory(CertificationLabelFactory)
    certification_status = factory.SubFactory(CertificationStatusFactory)
