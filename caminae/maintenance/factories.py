import factory

from caminae.core.factories import StakeFactory
from . import models


class InterventionStatusFactory(factory.Factory):
    FACTORY_FOR = models.InterventionStatus

    status = factory.Sequence(lambda n: u"Status %s" % n)


class InterventionDisorderFactory(factory.Factory):
    FACTORY_FOR = models.InterventionDisorder

    disorder = factory.Sequence(lambda n: u"Disorder %s" % n)


class InterventionTypologyFactory(factory.Factory):
    FACTORY_FOR = models.InterventionTypology

    typology = factory.Sequence(lambda n: u"Type %s" % n)


class InterventionJobFactory(factory.Factory):
    FACTORY_FOR = models.InterventionJob

    job = factory.Sequence(lambda n: u"Job %s" % n)


class ManDayFactory(factory.Factory):
    FACTORY_FOR = models.ManDay

    nb_days = 1
    job = factory.SubFactory(InterventionJobFactory)


class InterventionFactory(factory.Factory):
    FACTORY_FOR = models.Intervention

    status = factory.SubFactory(InterventionStatusFactory)
    stake = factory.SubFactory(StakeFactory)
    typology = factory.SubFactory(InterventionTypologyFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        intervention = super(InterventionFactory, cls)._prepare(create, **kwargs)
        if intervention.pk:
            intervention.disorders.add(InterventionDisorderFactory.create())
            ManDayFactory.create(intervention=intervention)
        return intervention
