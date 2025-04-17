import itertools

import factory
from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Polygon

from .. import models


def bbox_split(bbox, by_x=2, by_y=2, cycle=False):
    """Divide a box in rectangle, by_x parts and by_y parts"""
    minx, miny, maxx, maxy = bbox

    stepx = (maxx - minx) / by_x
    stepy = (maxy - miny) / by_y

    def gen():
        """define as inner function to decorate it with cycle"""
        stepx_tmp = minx
        while stepx_tmp + stepx <= maxx:
            stepx_next = stepx_tmp + stepx

            stepy_tmp = miny
            while stepy_tmp + stepy <= maxy:
                stepy_next = stepy_tmp + stepy
                yield (stepx_tmp, stepy_tmp, stepx_next, stepy_next)

                stepy_tmp = stepy_next

            stepx_tmp = stepx_next

    if cycle:
        return itertools.cycle(gen())
    else:
        return gen()


def bbox_split_srid_2154(*args, **kwargs):
    """Just round"""
    gen = bbox_split(*args, **kwargs)
    return iter(lambda: map(round, next(gen)), None)


# Don't intersect with geom from PathFactory
SPATIAL_EXTENT = (200000, 300000, 1100000, 1200000)

# Create 16 cities and 4 districts distinct same-area zone covering the spatial_extent and cycle on it
geom_city_iter = bbox_split_srid_2154(SPATIAL_EXTENT, by_x=4, by_y=4, cycle=True)
geom_district_iter = bbox_split_srid_2154(SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)
geom_area_iter = bbox_split_srid_2154(SPATIAL_EXTENT, by_x=2, by_y=2, cycle=True)


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.City

    code = factory.Sequence(lambda n: f"#{n}")  # id (!) with max_length=6
    name = factory.Faker("city")
    geom = factory.Sequence(
        lambda _: MultiPolygon(
            Polygon.from_bbox(next(geom_city_iter)), srid=settings.SRID
        )
    )


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.District

    name = factory.Faker("city")
    geom = factory.Sequence(
        lambda _: MultiPolygon(
            Polygon.from_bbox(next(geom_district_iter)), srid=settings.SRID
        )
    )


class RestrictedAreaTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RestrictedAreaType

    name = factory.Sequence(lambda n: f"Restricted area name {n}")


class RestrictedAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RestrictedArea

    name = factory.Sequence(lambda n: f"Restricted area name {n}")
    geom = factory.Sequence(
        lambda _: MultiPolygon(
            Polygon.from_bbox(next(geom_area_iter)), srid=settings.SRID
        )
    )
    area_type = factory.SubFactory(RestrictedAreaTypeFactory)
