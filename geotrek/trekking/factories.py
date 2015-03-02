# -*- coding: utf-8 -*-

import factory
from django.contrib.gis.geos import Point

from . import models
from geotrek.core.factories import TopologyFactory
from geotrek.common.utils.testdata import dummy_filefield_as_sequence


class TrekNetworkFactory(factory.Factory):
    FACTORY_FOR = models.TrekNetwork

    network = factory.Sequence(lambda n: u"network %s" % n)


class PracticeFactory(factory.Factory):
    FACTORY_FOR = models.Practice

    name = factory.Sequence(lambda n: u"usage %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class AccessibilityFactory(factory.Factory):
    FACTORY_FOR = models.Accessibility

    name = factory.Sequence(lambda n: u"accessibility %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class RouteFactory(factory.Factory):
    FACTORY_FOR = models.Route

    route = factory.Sequence(lambda n: u"route %s" % n)


class DifficultyLevelFactory(factory.Factory):
    FACTORY_FOR = models.DifficultyLevel

    difficulty = factory.Sequence(lambda n: u"difficulty %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class WebLinkCategoryFactory(factory.Factory):
    FACTORY_FOR = models.WebLinkCategory

    label = factory.Sequence(lambda n: u"Category %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class WebLinkFactory(factory.Factory):
    FACTORY_FOR = models.WebLink

    name = factory.Sequence(lambda n: u"web link name %s" % n)
    url = factory.Sequence(lambda n: u"http://dummy.url/%s" % n)
    category = factory.SubFactory(WebLinkCategoryFactory)


class TrekFactory(TopologyFactory):
    FACTORY_FOR = models.Trek

    name = factory.Sequence(lambda n: u"name %s" % n)
    departure = factory.Sequence(lambda n: u"departure %s" % n)
    arrival = factory.Sequence(lambda n: u"arrival %s" % n)
    published = True

    length = 10
    ascent = 0
    descent = 0
    min_elevation = 0
    max_elevation = 0

    description_teaser = factory.Sequence(lambda n: u"<p>description_teaser %s</p>" % n)
    description = factory.Sequence(lambda n: u"<p>description %s</p>" % n)
    ambiance = factory.Sequence(lambda n: u"<p>ambiance %s</p>" % n)
    access = factory.Sequence(lambda n: u"<p>access %s</p>" % n)
    disabled_infrastructure = factory.Sequence(lambda n: u"<p>disabled_infrastructure %s</p>" % n)
    # 60 minutes (1 hour)
    duration = 60

    is_park_centered = False

    advised_parking = factory.Sequence(lambda n: u"<p>Advised parking %s</p>" % n)
    parking_location = Point(1, 1)

    public_transport = factory.Sequence(lambda n: u"<p>Public transport %s</p>" % n)
    advice = factory.Sequence(lambda n: u"<p>Advice %s</p>" % n)

    route = factory.SubFactory(RouteFactory)
    difficulty = factory.SubFactory(DifficultyLevelFactory)
    practice = factory.SubFactory(PracticeFactory)


class TrekWithPOIsFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithPOIsFactory, cls)._prepare(create, **kwargs)
        path = trek.paths.all()[0]
        poi1 = POIFactory.create(no_path=True)
        poi1.add_path(path, start=0.5, end=0.5)
        poi2 = POIFactory.create(no_path=True)
        poi2.add_path(path, start=0.4, end=0.4)
        if create:
            trek.save()
        return trek


class TrekRelationshipFactory(factory.Factory):
    FACTORY_FOR = models.TrekRelationship

    has_common_departure = False
    has_common_edge = False
    is_circuit_step = False

    trek_a = factory.SubFactory(TrekFactory)
    trek_b = factory.SubFactory(TrekFactory)


class POITypeFactory(factory.Factory):
    FACTORY_FOR = models.POIType

    label = factory.Sequence(lambda n: u"POIType %s" % n)
    pictogram = dummy_filefield_as_sequence('pictogram %s')


class POIFactory(TopologyFactory):
    FACTORY_FOR = models.POI

    name = factory.Sequence(lambda n: u"POI %s" % n)
    description = factory.Sequence(lambda n: u"<p>description %s</p> % n)")
    type = factory.SubFactory(POITypeFactory)
    published = True
