# -*- coding: utf-8 -*-
import factory

from django.conf import settings
from django.contrib.gis.geos import Polygon, MultiPolygon

from mapentity.helpers import bbox_split_srid_2154

from geotrek.core.factories import TopologyFactory

from . import models


# Create 16 cities and 4 districts distinct same-area zone covering the spatial_extent and cycle on it
geom_city_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=4, by_y=4, cycle=True)
geom_district_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)
geom_area_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.City

    code = factory.Sequence(lambda n: u"#%s" % n)  # id (!) with max_length=6
    name = factory.Sequence(lambda n: u"City name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_city_iter.next()), srid=settings.SRID))


class DistrictFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.District

    name = factory.Sequence(lambda n: u"District name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_district_iter.next()), srid=settings.SRID))


class RestrictedAreaTypeFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.RestrictedAreaType

    name = factory.Sequence(lambda n: u"Restricted name %s" % n)


class RestrictedAreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.RestrictedArea

    name = factory.Sequence(lambda n: u"Restricted area name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_area_iter.next()), srid=settings.SRID))
    area_type = factory.SubFactory(RestrictedAreaTypeFactory)


class RestrictedAreaEdgeFactory(TopologyFactory):

    class Meta:
        model = models.RestrictedAreaEdge

    restricted_area = factory.SubFactory(RestrictedAreaFactory)


class CityEdgeFactory(TopologyFactory):

    class Meta:
        model = models.CityEdge

    city = factory.SubFactory(CityFactory)


class DistrictEdgeFactory(TopologyFactory):

    class Meta:
        model = models.DistrictEdge

    district = factory.SubFactory(DistrictFactory)
