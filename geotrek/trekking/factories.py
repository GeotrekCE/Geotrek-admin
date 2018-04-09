# -*- coding: utf-8 -*-

import factory
from django.contrib.gis.geos import Point

from . import models
from geotrek.core.factories import TopologyFactory, PointTopologyFactory
from geotrek.common.utils.testdata import dummy_filefield_as_sequence


class TrekNetworkFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TrekNetwork

    network = factory.Sequence(lambda n: "network %s" % n)


class PracticeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Practice

    name = factory.Sequence(lambda n: "usage %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class AccessibilityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Accessibility

    name = factory.Sequence(lambda n: "accessibility %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class RouteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Route

    route = factory.Sequence(lambda n: "route %s" % n)


class DifficultyLevelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.DifficultyLevel

    difficulty = factory.Sequence(lambda n: "difficulty %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class WebLinkCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WebLinkCategory

    label = factory.Sequence(lambda n: "Category %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class WebLinkFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WebLink

    name = factory.Sequence(lambda n: "web link name %s" % n)
    url = factory.Sequence(lambda n: "http://dummy.url/%s" % n)
    category = factory.SubFactory(WebLinkCategoryFactory)


class TrekFactory(TopologyFactory):
    class Meta:
        model = models.Trek

    name = factory.Sequence(lambda n: "name %s" % n)
    departure = factory.Sequence(lambda n: "departure %s" % n)
    arrival = factory.Sequence(lambda n: "arrival %s" % n)
    published = True

    length = 10
    ascent = 0
    descent = 0
    min_elevation = 0
    max_elevation = 0

    description_teaser = factory.Sequence(lambda n: "<p>description_teaser %s</p>" % n)
    description = factory.Sequence(lambda n: "<p>description %s</p>" % n)
    ambiance = factory.Sequence(lambda n: "<p>ambiance %s</p>" % n)
    access = factory.Sequence(lambda n: "<p>access %s</p>" % n)
    disabled_infrastructure = factory.Sequence(lambda n: "<p>disabled_infrastructure %s</p>" % n)
    duration = 1.5  # hour

    is_park_centered = False

    advised_parking = factory.Sequence(lambda n: "<p>Advised parking %s</p>" % n)
    parking_location = Point(1, 1)

    public_transport = factory.Sequence(lambda n: "<p>Public transport %s</p>" % n)
    advice = factory.Sequence(lambda n: "<p>Advice %s</p>" % n)

    route = factory.SubFactory(RouteFactory)
    difficulty = factory.SubFactory(DifficultyLevelFactory)
    practice = factory.SubFactory(PracticeFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        sources = kwargs.pop('sources', None)
        portals = kwargs.pop('portals', None)

        trek = super(TrekFactory, cls)._prepare(create, **kwargs)

        if create:
            if sources:
                for source in sources:
                    trek.source.add(source)

            if portals:
                for portal in portals:
                    trek.portal.add(portal)
        return trek


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


class TrekWithServicesFactory(TrekFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        trek = super(TrekWithServicesFactory, cls)._prepare(create, **kwargs)
        path = trek.paths.all()[0]
        service1 = ServiceFactory.create(no_path=True)
        service1.add_path(path, start=0.5, end=0.5)
        service1.type.practices.add(trek.practice)
        service2 = ServiceFactory.create(no_path=True)
        service2.add_path(path, start=0.4, end=0.4)
        service2.type.practices.add(trek.practice)
        if create:
            trek.save()
        return trek


class TrekRelationshipFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TrekRelationship

    has_common_departure = False
    has_common_edge = False
    is_circuit_step = False

    trek_a = factory.SubFactory(TrekFactory)
    trek_b = factory.SubFactory(TrekFactory)


class POITypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.POIType

    label = factory.Sequence(lambda n: "POIType %s" % n)
    pictogram = dummy_filefield_as_sequence('pictogram %s')


class POIFactory(PointTopologyFactory):
    class Meta:
        model = models.POI

    name = factory.Sequence(lambda n: "POI %s" % n)
    description = factory.Sequence(lambda n: "<p>description %s</p>" % n)
    type = factory.SubFactory(POITypeFactory)
    published = True


class ServiceTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ServiceType

    name = factory.Sequence(lambda n: "ServiceType %s" % n)
    pictogram = dummy_filefield_as_sequence('pictogram %s')
    published = True


class ServiceFactory(PointTopologyFactory):
    class Meta:
        model = models.Service

    type = factory.SubFactory(ServiceTypeFactory)
