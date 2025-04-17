import factory

from geotrek.common.tests.factories import OrganismFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.tests.factories import PointTopologyFactory

from .. import models


class SignageTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = "Signage type"
    pictogram = get_dummy_uploaded_image("signage_type.png")


class SignageTypeNoPictogramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SignageType

    label = "Signage type"


class BladeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BladeType

    label = "Blade type"


class BladeColorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Color

    label = "Blade color"


class BladeDirectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Direction

    label = "Blade direction"


class LineDirectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Direction

    label = "Line direction"


class SealingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Sealing

    label = "Sealing"


class SignageConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SignageCondition

    label = factory.Sequence(lambda n: f"Condition {n}")


class SignageFactory(PointTopologyFactory):
    class Meta:
        model = models.Signage

    name = "Signage"
    type = factory.SubFactory(SignageTypeFactory)
    manager = factory.SubFactory(OrganismFactory)
    sealing = factory.SubFactory(SealingFactory)
    printed_elevation = 4807
    published = True

    @factory.post_generation
    def conditions(obj, create, extracted=None, **kwargs):
        if create:
            if extracted:
                obj.conditions.set(extracted)
            else:
                obj.conditions.add(SignageConditionFactory.create())


class SignageNoPictogramFactory(SignageFactory):
    class Meta:
        model = models.Signage

    type = factory.SubFactory(SignageTypeNoPictogramFactory)


class BladeConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BladeCondition

    label = factory.Sequence(lambda n: f"Condition {n}")


class BladeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Blade

    number = factory.Sequence(lambda n: f"{n}")
    type = factory.SubFactory(BladeTypeFactory)
    direction = factory.SubFactory(BladeDirectionFactory)
    color = factory.SubFactory(BladeColorFactory)
    topology = factory.SubFactory(PointTopologyFactory)
    signage = factory.SubFactory(SignageFactory)

    @factory.post_generation
    def lines(obj, create, extracted=None, **kwargs):
        if create:
            LineFactory.create(blade=obj)

    @factory.post_generation
    def conditions(obj, create, extracted=None, **kwargs):
        if create:
            obj.conditions.add(BladeConditionFactory.create())


class LinePictogramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LinePictogram

    label = factory.Sequence(lambda n: f"Label {n}")
    code = factory.Sequence(lambda n: f"Code {n}")
    description = factory.Sequence(lambda n: f"Description {n}")


class LineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Line

    number = "1"
    direction = factory.SubFactory(LineDirectionFactory)
    text = "Text"
    distance = 42.5
    time = "0:42:30"
    blade = factory.SubFactory(BladeFactory)

    @factory.post_generation
    def pictograms(obj, create, extracted=None, **kwargs):
        if create:
            obj.pictograms.add(LinePictogramFactory.create())
