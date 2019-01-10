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


class SignageFactory(TopologyFactory):
    class Meta:
        model = models.Signage
    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(SignageTypeFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    published = True


class SignageNoPictogramFactory(TopologyFactory):
    class Meta:
        model = models.Signage
    name = factory.Sequence(lambda n: u"Signage %s" % n)
    type = factory.SubFactory(SignageTypeNoPictogramFactory)
    condition = factory.SubFactory(InfrastructureConditionFactory)
    published = True
