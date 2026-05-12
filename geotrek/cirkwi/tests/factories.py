import factory

from .. import models


class CirkwiLocomotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CirkwiLocomotion

    name = factory.Sequence(lambda n: f"Cirkwi Locomotion {n}")
