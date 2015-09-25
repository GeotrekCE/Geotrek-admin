import factory

from geotrek.core.factories import TopologyFactory

from . import models


class InfrastructureTypeFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


class InfrastructureConditionFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureCondition

    label = factory.Sequence(lambda n: u"State %s" % n)


class InfrastructureFactory(TopologyFactory):
    FACTORY_FOR = models.Infrastructure
    name = factory.Sequence(lambda n: u"Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)


class SignageFactory(TopologyFactory):
    FACTORY_FOR = models.Signage
    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory, type=models.INFRASTRUCTURE_TYPES.SIGNAGE)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    factory.SubFactory(InfrastructureTypeFactory)
