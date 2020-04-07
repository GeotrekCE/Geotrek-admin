import factory
from django.conf import settings
from django.contrib.gis.geos import Point

from . import models
from geotrek.core.factories import TopologyFactory, PointTopologyFactory
from geotrek.common.utils.testdata import dummy_filefield_as_sequence
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.signage.factories import SignageFactory


class TrekNetworkFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.TrekNetwork

    network = factory.Sequence(lambda n: "network %s" % n)
    pictogram = dummy_filefield_as_sequence('network-%s.png')


class PracticeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Practice

    name = factory.Sequence(lambda n: "usage %s" % n)
    pictogram = dummy_filefield_as_sequence('practice-%s.png')


class AccessibilityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Accessibility

    name = factory.Sequence(lambda n: "accessibility %s" % n)
    pictogram = dummy_filefield_as_sequence('accessibility-%s.png')


class RouteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Route

    route = factory.Sequence(lambda n: "route %s" % n)
    pictogram = dummy_filefield_as_sequence('route-%s.png')


class DifficultyLevelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.DifficultyLevel

    difficulty = factory.Sequence(lambda n: "difficulty %s" % n)
    pictogram = dummy_filefield_as_sequence('difficulty-%s.png')


class WebLinkCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WebLinkCategory

    label = factory.Sequence(lambda n: "Category %s" % n)
    pictogram = dummy_filefield_as_sequence('weblink-category-%s.png')


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
    geom = 'SRID=2154;LINESTRING (700000 6600000, 700100 6600100)'

    @factory.post_generation
    def sources(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for source in extracted:
                    obj.source.add(source)

    @factory.post_generation
    def portals(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                for portal in extracted:
                    obj.portal.add(portal)


class TrekWithPOIsFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_poi(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = obj.paths.all()[0]
            POIFactory.create(paths=[(path, 0.5, 0.5)])
            POIFactory.create(paths=[(path, 0.4, 0.4)])
            if create:
                obj.save()
        else:
            POIFactory.create(geom='SRID=2154;POINT (700040 6600040)')
            POIFactory.create(geom='SRID=2154;POINT (700050 6600050)')


class TrekWithPublishedPOIsFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_poi(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = obj.paths.all()[0]
            POIFactory.create(paths=[(path, 0.5, 0.5)], published=True, published_en=True, published_fr=True)
            POIFactory.create(paths=[(path, 0.4, 0.4)], published=True, published_en=True, published_fr=True)
            if create:
                obj.save()
        else:
            POIFactory.create(geom='SRID=2154;POINT (700040 6600040)',
                              published=True, published_en=True, published_fr=True)
            POIFactory.create(geom='SRID=2154;POINT (700050 6600050)',
                              published=True, published_en=True, published_fr=True)


class TrekWithInfrastructuresFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_infrastructures(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = obj.paths.all()[0]
            InfrastructureFactory.create(paths=[(path, 0.5, 0.5)])
            InfrastructureFactory.create(paths=[(path, 0.4, 0.4)])
            if create:
                obj.save()
        else:
            InfrastructureFactory.create(geom='SRID=2154;POINT (700040 6600040)')
            InfrastructureFactory.create(geom='SRID=2154;POINT (700050 6600050)')


class TrekWithSignagesFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_infrastructures(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = obj.paths.all()[0]
            SignageFactory.create(paths=[(path, 0.5, 0.5)])
            SignageFactory.create(paths=[(path, 0.4, 0.4)])
            if create:
                obj.save()
        else:
            SignageFactory.create(geom='SRID=2154;POINT (700040 6600040)')
            SignageFactory.create(geom='SRID=2154;POINT (700050 6600050)')


class TrekWithServicesFactory(TrekFactory):
    @factory.post_generation
    def create_trek_with_services(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = obj.paths.all()[0]
            service1 = ServiceFactory.create(paths=[(path, 0.5, 0.5)])
            service1.type.practices.add(obj.practice)
            service2 = ServiceFactory.create(paths=[(path, 0.4, 0.4)])
            service2.type.practices.add(obj.practice)
            if create:
                obj.save()
        else:
            service1 = ServiceFactory.create(geom='SRID=2154;POINT (700040 6600040)')
            service1.type.practices.add(obj.practice)
            service2 = ServiceFactory.create(geom='SRID=2154;POINT (700050 6600050)')
            service2.type.practices.add(obj.practice)


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
    pictogram = dummy_filefield_as_sequence('poi-type-%s.png')


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
    pictogram = dummy_filefield_as_sequence('service-type-%s.png')
    published = True


class ServiceFactory(PointTopologyFactory):
    class Meta:
        model = models.Service

    type = factory.SubFactory(ServiceTypeFactory)
