import factory

from geotrek.core.tests.factories import TopologyFactory
from geotrek.common.tests.factories import OrganismFactory

from .. import models


class PhysicalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PhysicalType

    name = factory.Sequence(lambda n: "PhysicalType %s" % n)


class PhysicalEdgeFactory(TopologyFactory):
    class Meta:
        model = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LandType

    name = factory.Sequence(lambda n: "LandType %s" % n)
    right_of_way = True


class LandEdgeFactory(TopologyFactory):
    class Meta:
        model = models.LandEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CirculationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CirculationType

    name = factory.Sequence(lambda n: "CirculationType %s" % n)


class CirculationEdgeFactory(TopologyFactory):
    class Meta:
        model = models.CirculationEdge

    circulation_type = factory.SubFactory(CirculationTypeFactory)


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
