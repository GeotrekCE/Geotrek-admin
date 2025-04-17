import factory

from geotrek.common.tests.factories import OrganismFactory
from geotrek.core.tests.factories import TopologyFactory

from .. import models


class PhysicalTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PhysicalType

    name = factory.Sequence(lambda n: f"PhysicalType {n}")


class PhysicalEdgeFactory(TopologyFactory):
    class Meta:
        model = models.PhysicalEdge

    physical_type = factory.SubFactory(PhysicalTypeFactory)


class LandTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LandType

    name = factory.Sequence(lambda n: f"LandType {n}")
    right_of_way = True


class LandEdgeFactory(TopologyFactory):
    class Meta:
        model = models.LandEdge

    land_type = factory.SubFactory(LandTypeFactory)


class CirculationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CirculationType

    name = factory.Sequence(lambda n: f"CirculationType {n}")


class AuthorizationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AuthorizationType

    name = factory.Sequence(lambda n: f"AuthorizationType {n}")


class CirculationEdgeFactory(TopologyFactory):
    class Meta:
        model = models.CirculationEdge

    circulation_type = factory.SubFactory(CirculationTypeFactory)
    authorization_type = factory.SubFactory(AuthorizationTypeFactory)


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
