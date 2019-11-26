from django.conf import settings
from django.contrib.gis.geos import Point

import factory

from geotrek.feedback import models as feedback_models


class ReportCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportCategory

    category = factory.Sequence(lambda n: "Category %s" % n)


class ReportStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportStatus

    status = factory.Sequence(lambda n: "Status %s" % n)


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.Report

    name = factory.Sequence(lambda n: "name %s" % n)
    email = factory.Sequence(lambda n: "email%s@domain.tld" % n)
    comment = factory.Sequence(lambda n: "comment %s" % n)
    geom = Point(700000, 6600000, srid=settings.SRID)
