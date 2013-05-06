import factory

from geotrek.core.factories import StakeFactory
from geotrek.common.factories import OrganismFactory
from geotrek.infrastructure.factories import InfrastructureFactory
from . import models


class InterventionStatusFactory(factory.Factory):
    FACTORY_FOR = models.InterventionStatus

    status = factory.Sequence(lambda n: u"Status %s" % n)


class InterventionDisorderFactory(factory.Factory):
    FACTORY_FOR = models.InterventionDisorder

    disorder = factory.Sequence(lambda n: u"Disorder %s" % n)


class InterventionTypeFactory(factory.Factory):
    FACTORY_FOR = models.InterventionType

    type = factory.Sequence(lambda n: u"Type %s" % n)


class InterventionJobFactory(factory.Factory):
    FACTORY_FOR = models.InterventionJob

    job = factory.Sequence(lambda n: u"Job %s" % n)
    cost = 500.0


class ManDayFactory(factory.Factory):
    FACTORY_FOR = models.ManDay

    nb_days = 1
    job = factory.SubFactory(InterventionJobFactory)


class InterventionFactory(factory.Factory):
    FACTORY_FOR = models.Intervention

    status = factory.SubFactory(InterventionStatusFactory)
    stake = factory.SubFactory(StakeFactory)
    type = factory.SubFactory(InterventionTypeFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        intervention = super(InterventionFactory, cls)._prepare(create, **kwargs)
        if intervention.pk:
            intervention.disorders.add(InterventionDisorderFactory.create())
            ManDayFactory.create(intervention=intervention)
        return intervention


class InfrastructureInterventionFactory(InterventionFactory):
    @classmethod
    def _prepare(cls, create, **kwargs):
        intervention = super(InfrastructureInterventionFactory, cls)._prepare(create, **kwargs)
        infra = InfrastructureFactory.create()
        intervention.set_infrastructure(infra)
        if create:
            intervention.save()
        return intervention


class ContractorFactory(factory.Factory):
    FACTORY_FOR = models.Contractor

    contractor = factory.Sequence(lambda n: u"Contractor %s" % n)


class ProjectTypeFactory(factory.Factory):
    FACTORY_FOR = models.ProjectType

    type = factory.Sequence(lambda n: u"Type %s" % n)


class ProjectDomainFactory(factory.Factory):
    FACTORY_FOR = models.ProjectDomain

    domain = factory.Sequence(lambda n: u"Domain %s" % n)


class ProjectFactory(factory.Factory):
    FACTORY_FOR = models.Project

    name = factory.Sequence(lambda n: u"Project %s" % n)
    type = factory.SubFactory(ProjectTypeFactory)
    domain = factory.SubFactory(ProjectDomainFactory)
    begin_year = 2010
    end_year = 2012
    project_owner = factory.SubFactory(OrganismFactory)
    project_manager = factory.SubFactory(OrganismFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        project = super(ProjectFactory, cls)._prepare(create, **kwargs)
        if project.pk:
            project.contractors.add(ContractorFactory.create())
            FundingFactory.create(project=project)
        return project


class FundingFactory(factory.Factory):
    FACTORY_FOR = models.Funding

    project = factory.SubFactory(ProjectFactory)
    organism = factory.SubFactory(OrganismFactory)
