import factory

from geotrek.common.utils.testdata import dummy_filefield_as_sequence
from geotrek.core.tests.factories import PointTopologyFactory, TopologyFactory

from .. import models


class InfrastructureTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InfrastructureType

    label = factory.Sequence(lambda n: "Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING
    pictogram = dummy_filefield_as_sequence('infrastructure-type-%s.png')


class InfrastructureTypeNoPictogramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InfrastructureType

    label = factory.Sequence(lambda n: "Type %s" % n)
    type = models.INFRASTRUCTURE_TYPES.BUILDING


class InfrastructureConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InfrastructureCondition

    label = factory.Sequence(lambda n: "Condition %s" % n)


class InfrastructureUsageDifficultyLevelFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.InfrastructureUsageDifficultyLevel
    label = factory.Sequence(lambda n: "Usage level %s" % n)


class InfrastructureMaintenanceDifficultyLevelFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.InfrastructureMaintenanceDifficultyLevel
    label = factory.Sequence(lambda n: "Maintenance level %s" % n)


class InfrastructureFactoryMixin():
    @factory.post_generation
    def conditions(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                obj.conditions.set(extracted)
            else:
                obj.conditions.add(InfrastructureConditionFactory.create())


class InfrastructureFactory(TopologyFactory, InfrastructureFactoryMixin):
    class Meta:
        model = models.Infrastructure
    name = factory.Sequence(lambda n: "Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)
    published = True
    usage_difficulty = factory.SubFactory(InfrastructureUsageDifficultyLevelFactory)
    maintenance_difficulty = factory.SubFactory(InfrastructureMaintenanceDifficultyLevelFactory)


class PointInfrastructureFactory(PointTopologyFactory, InfrastructureFactoryMixin):
    class Meta:
        model = models.Infrastructure
    name = factory.Sequence(lambda n: "Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeFactory)
    published = True


class InfrastructureNoPictogramFactory(TopologyFactory, InfrastructureFactoryMixin):
    class Meta:
        model = models.Infrastructure
    name = factory.Sequence(lambda n: "Infrastructure %s" % n)
    type = factory.SubFactory(InfrastructureTypeNoPictogramFactory)
    published = True
