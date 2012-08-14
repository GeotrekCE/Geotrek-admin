# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import TopologyMixinFactory, TopologyMixinKindFactory
from . import models


class InfrastructureTypeFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


class InfrastructureFactory(factory.Factory):
    FACTORY_FOR = models.Infrastructure

    topo_object = factory.SubFactory(TopologyMixinFactory)
    name = factory.Sequence(lambda n: u"Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)



class SignageFactory(factory.Factory):
    FACTORY_FOR = models.Signage

    topo_object = factory.SubFactory(TopologyMixinFactory)
    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory, type=models.INFRASTRUCTURE_TYPES.SIGNAGE)
