import factory
from . import models


class InterventionStatusFactory(factory.Factory):
    FACTORY_FOR = models.InterventionStatus

    status = factory.Sequence(lambda n: u"Status %s" % n)


class InterventionFactory(factory.Factory):
    FACTORY_FOR = models.Intervention

    status = factory.SubFactory(InterventionStatusFactory)
