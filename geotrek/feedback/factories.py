from django.conf import settings
from django.contrib.gis.geos import Point

import factory

from geotrek.feedback import models as feedback_models


class ReportActivityFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportActivity

    label = factory.Sequence(lambda n: "Activity %s" % n)


class ReportCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportCategory

    label = factory.Sequence(lambda n: "Category %s" % n)


class ReportStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportStatus

    label = factory.Sequence(lambda n: "Status %s" % n)


class ReportProblemMagnitudeFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportProblemMagnitude

    label = factory.Sequence(lambda n: "Utilisation %s" % n)


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.Report

    email = factory.Sequence(lambda n: "email%s@domain.tld" % n)
    comment = factory.Sequence(lambda n: "comment %s" % n)
    geom = Point(700000, 6600000, srid=settings.SRID)
    activity = factory.SubFactory(ReportActivityFactory)
    problem_magnitude = factory.SubFactory(ReportProblemMagnitudeFactory)
    category = factory.SubFactory(ReportCategoryFactory)
