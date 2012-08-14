# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import TopologyMixinFactory
from . import models


class InfrastructureTypeFactory(factory.Factory):
    FACTORY_FOR = models.InfrastructureType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


class InfrastructureFactory(TopologyMixinFactory):
    FACTORY_FOR = models.Infrastructure

    name = factory.Sequence(lambda n: u"Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)


class SignageFactory(TopologyMixinFactory):
    FACTORY_FOR = models.Signage

    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)
