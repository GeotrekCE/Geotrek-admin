# -*- coding: utf-8 -*-

import factory
from django.contrib.gis.geos import Point, LineString

from . import models
from caminae.utils.testdata import get_dummy_uploaded_image


def dummy_filefield_as_sequence(toformat_name):
    """Simple helper method to fill a models.FileField"""
    return factory.Sequence(lambda n: get_dummy_uploaded_image(toformat_name % n))


class TrekNetworkFactory(factory.Factory):
    FACTORY_FOR = models.TrekNetwork

    network = factory.Sequence(lambda n: u"network %s" % n)


class UsageFactory(factory.Factory):
    FACTORY_FOR = models.Usage

    usage = factory.Sequence(lambda n: u"usage %s" % n)


class RouteFactory(factory.Factory):
    FACTORY_FOR = models.Route

    route = factory.Sequence(lambda n: u"route %s" % n)


class DifficultyLevelFactory(factory.Factory):
    FACTORY_FOR = models.DifficultyLevel

    difficulty = factory.Sequence(lambda n: u"difficulty %s" % n)


class DestinationFactory(factory.Factory):
    FACTORY_FOR = models.Destination

    destination = factory.Sequence(lambda n: u"destination %s" % n)
    pictogram =  dummy_filefield_as_sequence('pictogram %s')


class WebLinkFactory(factory.Factory):
    FACTORY_FOR = models.WebLink

    name = factory.Sequence(lambda n: u"web link name %s" % n)
    url = factory.Sequence(lambda n: u"http://dummy.url/%s" % n)

    thumbnail = dummy_filefield_as_sequence('thumbnail %s')


class TrekFactory(factory.Factory):
    FACTORY_FOR = models.Trek

    name = factory.Sequence(lambda n: u"name %s" % n)
    departure = factory.Sequence(lambda n: u"departure %s" % n)
    arrival = factory.Sequence(lambda n: u"arrival %s" % n)
    validated = True

    length = 10
    ascent = 0
    descent = 0
    min_elevation = 0
    max_elevation = 0

    description_teaser = factory.Sequence(lambda n: u"description_teaser %s" % n)
    description = factory.Sequence(lambda n: u"description %s" % n)
    ambiance = factory.Sequence(lambda n: u"ambiance %s" % n)
    handicapped_infrastructure = factory.Sequence(lambda n: u"handicapped_infrastructure %s" % n)
    # 60 minutes (1 hour)
    duration = 60

    is_park_centered = False
    is_transborder = False

    advised_parking = factory.Sequence(lambda n: u"Advised parking %s" % n)
    parking_location = Point(1, 1)

    public_transport = factory.Sequence(lambda n: u"Public transport %s" % n)
    advice = factory.Sequence(lambda n: u"Advice %s" % n)

    geom = LineString(Point(1, 1, 0), Point(2, 2, 0))

    # do not populate insert_date / update_date

    deleted = False

    route = factory.SubFactory(RouteFactory)
    difficulty = factory.SubFactory(DifficultyLevelFactory)
    destination = factory.SubFactory(DestinationFactory)


class TrekRelationshipFactory(factory.Factory):
    FACTORY_FOR = models.TrekRelationship

    has_common_departure = False
    has_common_edge = False
    is_circuit_step = False

    trek_a = factory.SubFactory(TrekFactory)
    trek_b = factory.SubFactory(TrekFactory)


