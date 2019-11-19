import factory

from geotrek.common.utils.testdata import dummy_filefield_as_sequence
from geotrek.core.factories import PointTopologyFactory
from geotrek.infrastructure.factories import InfrastructureConditionFactory

from . import models


class SignageTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = factory.Sequence(lambda n: "Type %s" % n)
    pictogram = dummy_filefield_as_sequence('signage-type-%s.png')


class SignageTypeNoPictogramFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = factory.Sequence(lambda n: "Type %s" % n)


class BladeTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BladeType

    label = factory.Sequence(lambda n: "Type %s" % n)


class BladeColorFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Color

    label = factory.Sequence(lambda n: "Color %s" % n)


class BladeDirectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Direction

    label = factory.Sequence(lambda n: "Direction %s" % n)


class SealingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Sealing

    label = factory.Sequence(lambda n: "Sealing %s" % n)


class SignageFactory(PointTopologyFactory):
    class Meta:
        model = models.Signage

    name = factory.Sequence(lambda n: "Signage %s" % n)
    type = factory.SubFactory(SignageTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    sealing = factory.SubFactory(SealingFactory)
    printed_elevation = factory.Sequence(lambda n: "%d" % n)
    published = True


class SignageNoPictogramFactory(PointTopologyFactory):
    class Meta:
        model = models.Signage

    name = factory.Sequence(lambda n: "Signage %s" % n)
    type = factory.SubFactory(SignageTypeNoPictogramFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    published = True


class BladeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Blade

    number = factory.Sequence(lambda n: "%d" % n)
    type = factory.SubFactory(BladeTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    direction = factory.SubFactory(BladeDirectionFactory)
    color = factory.SubFactory(BladeColorFactory)
    topology = factory.SubFactory(PointTopologyFactory)
    signage = factory.SubFactory(SignageFactory)

    @factory.post_generation
    def lines(obj, create, extracted=None, **kwargs):
        if create:
            LineFactory.create(blade=obj)


class LineFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Line

    number = factory.Sequence(lambda n: "%d" % n)
    text = factory.Sequence(lambda n: "Text %s" % n)
    distance = factory.Sequence(lambda n: "%d" % 10)
    pictogram_name = factory.Sequence(lambda n: "Pictogram %s" % n)
    time = factory.Sequence(lambda n: "%s:%s:%s" % (n, n + 1, n + 2))
    blade = factory.SubFactory(BladeFactory)
