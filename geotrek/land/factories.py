# -*- coding: utf-8 -*-
import factory

from geotrek.core.factories import TopologyFactory
from geotrek.common.factories import OrganismFactory

from . import models


class PhysicalTypeFactory(factory.Factory):
    FACTORY_FOR = models.PhysicalType

    name = factory.Sequence(lambda n: u"PhysicalType %s" % n)


class PhysicalEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(factory.Factory):
    FACTORY_FOR = models.LandType

    name = factory.Sequence(lambda n: u"LandType %s" % n)
    right_of_way = True


class LandEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.LandEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CompetenceEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.CompetenceEdge

    organization = factory.SubFactory(OrganismFactory)


class WorkManagementEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)


class SignageManagementEdgeFactory(TopologyFactory):
    FACTORY_FOR = models.SignageManagementEdge

    organization = factory.SubFactory(OrganismFactory)
