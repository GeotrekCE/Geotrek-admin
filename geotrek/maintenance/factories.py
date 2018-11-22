import factory

from geotrek.core.factories import PathFactory, StakeFactory
from geotrek.common.factories import OrganismFactory
from geotrek.infrastructure.factories import InfrastructureFactory, SignageFactory
from . import models


class InterventionStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InterventionStatus

    status = factory.Sequence(lambda n: "Status %s" % n)


class InterventionDisorderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InterventionDisorder

    disorder = factory.Sequence(lambda n: "Disorder %s" % n)


class InterventionTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InterventionType

    type = factory.Sequence(lambda n: "Type %s" % n)


class InterventionJobFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InterventionJob

    job = factory.Sequence(lambda n: "Job %s" % n)
    cost = 500.0


class ManDayFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ManDay

    nb_days = 1
    job = factory.SubFactory(InterventionJobFactory)


class InterventionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Intervention

    name = factory.Sequence(lambda n: "Intervention %s" % n)
    status = factory.SubFactory(InterventionStatusFactory)
    stake = factory.SubFactory(StakeFactory)
    type = factory.SubFactory(InterventionTypeFactory)

    @factory.post_generation
    def create_intervention(obj, create, extracted, **kwargs):
        if obj.pk:
            obj.disorders.add(InterventionDisorderFactory.create())
            ManDayFactory.create(intervention=obj)


class InfrastructureInterventionFactory(InterventionFactory):
    @factory.post_generation
    def create_infrastructure_intervention(obj, create, extracted, **kwargs):
        infra = InfrastructureFactory.create()
        obj.set_infrastructure(infra)
        if create:
            obj.save()


class InfrastructurePointInterventionFactory(InterventionFactory):
    @factory.post_generation
    def create_infrastructure_point_intervention(obj, create, extracted, **kwargs):
        infra = InfrastructureFactory.create(no_path=True)
        infra.add_path(PathFactory.create(), start=0.5, end=0.5)
        obj.set_infrastructure(infra)
        if create:
            obj.save()


class SignageInterventionFactory(InterventionFactory):
    @factory.post_generation
    def create_signage_intervention(obj, create, extracted, **kwargs):
        infra = SignageFactory.create()
        obj.set_infrastructure(infra)
        if create:
            obj.save()


class ContractorFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Contractor

    contractor = factory.Sequence(lambda n: "Contractor %s" % n)


class ProjectTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ProjectType

    type = factory.Sequence(lambda n: "Type %s" % n)


class ProjectDomainFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ProjectDomain

    domain = factory.Sequence(lambda n: "Domain %s" % n)


class ProjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Project

    name = factory.Sequence(lambda n: "Project %s" % n)
    type = factory.SubFactory(ProjectTypeFactory)
    domain = factory.SubFactory(ProjectDomainFactory)
    begin_year = 2010
    end_year = 2012
    project_owner = factory.SubFactory(OrganismFactory)
    project_manager = factory.SubFactory(OrganismFactory)

    @factory.post_generation
    def create_project(obj, create, extracted, **kwargs):
        if create:
            obj.contractors.add(ContractorFactory.create())
            FundingFactory.create(project=obj)


class FundingFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Funding

    project = factory.SubFactory(ProjectFactory)
    organism = factory.SubFactory(OrganismFactory)
