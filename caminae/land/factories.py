# -*- coding: utf-8 -*-

import factory

from django.conf import settings
from django.contrib.gis.geos import Polygon, MultiPolygon

from caminae.core.factories import TopologyFactory
from caminae.common.factories import OrganismFactory
from caminae.mapentity.helpers import bbox_split_srid_2154

from . import models


class PhysicalTypeFactory(factory.Factory):
    FACTORY_FOR = models.PhysicalType

    name = factory.Sequence(lambda n: u"PhysicalType %s" % n)


class PhysicalEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(factory.Factory):
    FACTORY_FOR = models.LandType

    name = factory.Sequence(lambda n: u"LandType %s" % n)
    right_of_way = True


class LandEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.LandEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CompetenceEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.CompetenceEdge

    organization = factory.SubFactory(OrganismFactory)


class WorkManagementEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)


class SignageManagementEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.SignageManagementEdge

    organization = factory.SubFactory(OrganismFactory)



# Create 16 cities and 4 districts distinct same-area zone covering the spatial_extent and cycle on it
geom_city_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=4, by_y=4, cycle=True)
geom_district_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)
geom_area_iter = bbox_split_srid_2154(settings.SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)

class CityFactory(factory.Factory):
    FACTORY_FOR = models.City

    code = factory.Sequence(lambda n: u"#%s" % n) # id (!) with max_length=6
    name = factory.Sequence(lambda n: u"City name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_city_iter.next()), srid=settings.SRID))


class DistrictFactory(factory.Factory):
    FACTORY_FOR = models.District

    name = factory.Sequence(lambda n: u"District name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_district_iter.next()), srid=settings.SRID))


class RestrictedAreaTypeFactory(factory.Factory):

    FACTORY_FOR = models.RestrictedAreaType

    name = factory.Sequence(lambda n: u"Restricted name %s" % n)


class RestrictedAreaFactory(factory.Factory):
    FACTORY_FOR = models.RestrictedArea

    name = factory.Sequence(lambda n: u"Restricted area name %s" % n)
    geom = factory.Sequence(lambda _: MultiPolygon(Polygon.from_bbox(geom_area_iter.next()), srid=settings.SRID))
    area_type = factory.SubFactory(RestrictedAreaTypeFactory)


class RestrictedAreaEdgeFactory(TopologyFactory):

    FACTORY_FOR = models.RestrictedAreaEdge

    restricted_area = factory.SubFactory(RestrictedAreaFactory)


class CityEdgeFactory(TopologyFactory):

    FACTORY_FOR = models.CityEdge

    city = factory.SubFactory(CityFactory)


class DistrictEdgeFactory(TopologyFactory):

    FACTORY_FOR = models.DistrictEdge

    district = factory.SubFactory(DistrictFactory)
