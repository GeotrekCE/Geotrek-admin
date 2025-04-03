import factory
from django.conf import settings
from django.contrib.gis.geos import Point

from geotrek.feedback import models as feedback_models


class ReportStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportStatus

    label = factory.Sequence(lambda n: "Status %s" % n)
    identifier = factory.Sequence(lambda n: "ID %s" % n)


class ReportActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportActivity

    label = factory.Sequence(lambda n: "Activity %s" % n)


class ReportCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportCategory

    label = factory.Sequence(lambda n: "Category %s" % n)


class PredefinedEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.PredefinedEmail

    label = factory.Sequence(lambda n: "Predefined Email %s" % n)
    text = factory.Sequence(lambda n: "Some email body content %s" % n)


class ReportProblemMagnitudeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportProblemMagnitude

    label = factory.Sequence(lambda n: "Utilisation %s" % n)


class WorkflowManagerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.WorkflowManager


class WorkflowDistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.WorkflowDistrict


class ReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.Report

    email = factory.Sequence(lambda n: "email%s@domain.tld" % n)
    comment = factory.Sequence(lambda n: "comment %s" % n)
    geom = Point(700000, 6600000, srid=settings.SRID)
    activity = factory.SubFactory(ReportActivityFactory)
    problem_magnitude = factory.SubFactory(ReportProblemMagnitudeFactory)
    category = factory.SubFactory(ReportCategoryFactory)
    status = factory.SubFactory(ReportStatusFactory)
    eid = factory.Sequence(lambda n: n)


class TimerEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = feedback_models.TimerEvent
