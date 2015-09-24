import factory

from geotrek.core.factories import TopologyFactory

from . import models


class InfrastructureTypeFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


class InfrastructureStateFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureState

    label = factory.Sequence(lambda n: u"State %s" % n)


class InfrastructureFactory(TopologyFactory):
    FACTORY_FOR = models.Infrastructure
    name = factory.Sequence(lambda n: u"Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)
    state = factory.SubFactory(InfrastructureStateFactory)


class SignageFactory(TopologyFactory):
    FACTORY_FOR = models.Signage
    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory, type=models.INFRASTRUCTURE_TYPES.SIGNAGE)
    factory.SubFactory(InfrastructureTypeFactory)
