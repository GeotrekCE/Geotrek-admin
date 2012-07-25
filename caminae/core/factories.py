import factory
from django.contrib.gis.geos import Point, LineString

from . import models
from caminae.utils.testdata import get_dummy_uploaded_image
from django.conf import settings


class DatasourceManagementFactory(factory.Factory):
    FACTORY_FOR = models.DatasourceManagement

    source = factory.Sequence(lambda n: u"Datasource %s" % n)


class ChallengeManagementFactory(factory.Factory):
    FACTORY_FOR = models.ChallengeManagement

    challenge = factory.Sequence(lambda n: u"Challenge %s" % n)


class UsageManagementFactory(factory.Factory):
    FACTORY_FOR = models.UsageManagement

    usage = factory.Sequence(lambda n: u"Usage %s" % n)


class NetworkManagementFactory(factory.Factory):
    FACTORY_FOR = models.NetworkManagement

    network = factory.Sequence(lambda n: u"Usage %s" % n)


class PathManagementFactory(factory.Factory):
    FACTORY_FOR = models.PathManagement

    name =  factory.Sequence(lambda n: u"Name %s" % n)
    departure =  factory.Sequence(lambda n: u"Departure %s" % n)
    arrival =  factory.Sequence(lambda n: u"Arrival %s" % n)
    comments =  factory.Sequence(lambda n: u"Comments %s" % n)


class PathFactory(factory.Factory):
    FACTORY_FOR = models.Path

    geom = LineString(Point(1, 1), Point(2, 2), srid=settings.SRID)
    geom_cadastre = LineString(Point(5, 5), Point(6, 6), srid=settings.SRID)
    valid = True
    name = factory.Sequence(lambda n: u"name %s" % n)
    comments = factory.Sequence(lambda n: u"comment %s" % n)

    # Trigger computed values are not provided:
    # date_insert/date_update/length/ascent/descent/min_elevation/max_elevation/

    # FK that could also be null
    path_management = factory.SubFactory(PathManagementFactory)
    datasource_management = factory.SubFactory(DatasourceManagementFactory)
    challenge_management = factory.SubFactory(ChallengeManagementFactory)


class TopologyMixinKindFactory(factory.Factory):
    FACTORY_FOR = models.TopologyMixinKind

    kind = factory.Sequence(lambda n: u"Kind %s" % n)


class TopologyMixinFactory(factory.Factory):
    FACTORY_FOR = models.TopologyMixin

    # Factory
    # troncons (M2M)
    offset = 1
    deleted = False
    kind = factory.SubFactory(TopologyMixinKindFactory)

    # Trigger computed values are not provided:
    # date_insert/date_update/length/geom/

    # FIXME: remove this when the trigger will be ready
    length = 0
    geom = LineString(Point(1, 1), Point(2, 2), srid=settings.SRID)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """
        A topology mixin should be linked to at least one Path (through
        PathAggregation).
        """

        topo_mixin = super(TopologyMixinFactory, cls)._prepare(create, **kwargs)
        if create:
            PathAggregationFactory.create(topo_object=topo_mixin)
        else:
            PathAggregationFactory.build(topo_object=topo_mixin)
        return topo_mixin


class PathAggregationFactory(factory.Factory):
    FACTORY_FOR = models.PathAggregation

    path = factory.SubFactory(PathFactory)
    topo_object = factory.SubFactory(TopologyMixinFactory)

    start_position = 1.0
    end_position = 2.0


