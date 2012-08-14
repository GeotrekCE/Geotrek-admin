# -*- coding: utf-8 -*-

import factory

from caminae.core.factories import TopologyMixinFactory
from caminae.common.factories import OrganismFactory
from . import models


class PhysicalTypeFactory(factory.Factory):
    FACTORY_FOR = models.PhysicalType

    name = factory.Sequence(lambda n: u"PhysicalType %s" % n)


class PhysicalEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.LandType

    name = factory.Sequence(lambda n: u"LandType %s" % n)
    right_of_way = True


class LandEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.PhysicalEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CompetenceEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)


class WorkManagementEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)


class SignageManagementEdgeFactory(TopologyMixinFactory):
    FACTORY_FOR = models.SignageManagementEdge

    organization = factory.SubFactory(OrganismFactory)
