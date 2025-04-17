import factory
from django.conf import settings

from geotrek.common.tests.factories import OrganismFactory
from geotrek.core.tests.factories import PathFactory, StakeFactory, TopologyFactory
from geotrek.feedback.tests.factories import ReportFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.signage.tests.factories import SignageFactory

from .. import models


class InterventionStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InterventionStatus

    status = factory.Sequence(lambda n: f"Status {n}")


class InterventionDisorderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InterventionDisorder

    disorder = factory.Sequence(lambda n: f"Disorder {n}")


class InterventionTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InterventionType

    type = factory.Sequence(lambda n: f"Type {n}")


class InterventionJobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.InterventionJob

    job = factory.Sequence(lambda n: f"Job {n}")
    cost = 500.0


class ManDayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ManDay

    nb_days = 1
    job = factory.SubFactory(InterventionJobFactory)


class LightInterventionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Intervention

    name = factory.Sequence(lambda n: f"Intervention {n}")
    status = factory.SubFactory(InterventionStatusFactory)
    stake = factory.SubFactory(StakeFactory)
    type = factory.SubFactory(InterventionTypeFactory)
    target = factory.SubFactory(TopologyFactory)


class InterventionFactory(LightInterventionFactory):
    begin_date = "2022-03-30"

    @factory.post_generation
    def create_intervention(obj, create, extracted, **kwargs):
        if obj.pk:
            obj.disorders.add(InterventionDisorderFactory.create())
            ManDayFactory.create(intervention=obj)


class InfrastructureInterventionFactory(InterventionFactory):
    target = factory.SubFactory(InfrastructureFactory)


class ReportInterventionFactory(InterventionFactory):
    target = factory.SubFactory(ReportFactory)


class InfrastructurePointInterventionFactory(InterventionFactory):
    target = None

    @factory.post_generation
    def create_infrastructure_point_intervention(obj, create, extracted, **kwargs):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            infra = InfrastructureFactory.create(
                paths=[(PathFactory.create(), 0.5, 0.5)]
            )

        else:
            infra = InfrastructureFactory.create(
                geom="SRID=2154;POINT (700040 6600040)"
            )
        obj.target = infra
        if create:
            obj.save()


class SignageInterventionFactory(InterventionFactory):
    target = factory.SubFactory(SignageFactory)


class ContractorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Contractor

    contractor = factory.Sequence(lambda n: f"Contractor {n}")


class ProjectTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProjectType

    type = factory.Sequence(lambda n: f"Type {n}")


class ProjectDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProjectDomain

    domain = factory.Sequence(lambda n: f"Domain {n}")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Project

    name = factory.Sequence(lambda n: f"Project {n}")
    begin_year = 2010

    @factory.post_generation
    def create_project(obj, create, extracted, **kwargs):
        if create:
            obj.contractors.add(ContractorFactory.create())
            FundingFactory.create(project=obj, amount=1000)


class ProjectWithInterventionFactory(ProjectFactory):
    @factory.post_generation
    def create_project(obj, create, extracted, **kwargs):
        if create:
            obj.contractors.add(ContractorFactory.create())
            FundingFactory.create(project=obj, amount=1000)
            InfrastructureInterventionFactory.create(project=obj)


class FundingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Funding

    project = factory.SubFactory(ProjectFactory)
    organism = factory.SubFactory(OrganismFactory)
