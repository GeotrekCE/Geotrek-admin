# -*- coding: utf-8 -*-
import factory

from geotrek.core.factories import TopologyFactory
from geotrek.common.factories import OrganismFactory

from . import models


class PhysicalTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PhysicalType

    name = factory.Sequence(lambda n: u"PhysicalType %s" % n)


class PhysicalEdgeFactory(TopologyFactory):
    class Meta:
        model = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.LandType

    name = factory.Sequence(lambda n: u"LandType %s" % n)
    right_of_way = True


class LandEdgeFactory(TopologyFactory):
    class Meta:
        model = models.LandEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CompetenceEdgeFactory(TopologyFactory):
    class Meta:
        model = models.CompetenceEdge

    organization = factory.SubFactory(OrganismFactory)


class WorkManagementEdgeFactory(TopologyFactory):
    class Meta:
        model = models.WorkManagementEdge

    organization = factory.SubFactory(OrganismFactory)


class SignageManagementEdgeFactory(TopologyFactory):
    class Meta:
        model = models.SignageManagementEdge

    organization = factory.SubFactory(OrganismFactory)
