import factory

from geotrek.common.utils.testdata import dummy_filefield_as_sequence
from geotrek.core.factories import TopologyFactory
from geotrek.infrastructure.factories import InfrastructureConditionFactory

from . import models


class SignageTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = factory.Sequence(lambda n: u"Type %s" % n)
    pictogram = dummy_filefield_as_sequence('thumbnail %s')


class SignageTypeNoPictogramFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = factory.Sequence(lambda n: u"Type %s" % n)


class BladeTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BladeType

    label = factory.Sequence(lambda n: u"Type %s" % n)


class BladeColorFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Color

    label = factory.Sequence(lambda n: u"Color %s" % n)


class BladeDirectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Direction

    label = factory.Sequence(lambda n: u"Direction %s" % n)


class SealingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Sealing

    label = factory.Sequence(lambda n: u"Sealing %s" % n)


class SignageFactory(TopologyFactory):
    class Meta:
        model = models.Signage

    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(SignageTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    sealing = factory.SubFactory(SealingFactory)
    printed_elevation = factory.Sequence(lambda n: u"%d" % n)
    published = True


class SignageNoPictogramFactory(TopologyFactory):
    class Meta:
        model = models.Signage

    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(SignageTypeNoPictogramFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    published = True


class BladeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Blade

    number = factory.Sequence(lambda n: u"%d" % n)
    type = factory.SubFactory(BladeTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    direction = factory.SubFactory(BladeDirectionFactory)
    color = factory.SubFactory(BladeColorFactory)
    topology = factory.SubFactory(TopologyFactory)
    signage = factory.SubFactory(SignageFactory)


class LineFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Line

    number = factory.Sequence(lambda n: u"%d" % n)
    text = factory.Sequence(lambda n: u"Text %s" % n)
    distance = factory.Sequence(lambda n: u"%d" % 10)
    pictogram_name = factory.Sequence(lambda n: u"Pictogram %s" % n)
    time = factory.Sequence(lambda n: u"%s:%s:%s" % (n, n+1, n+2))
    blade = factory.SubFactory(BladeFactory)
