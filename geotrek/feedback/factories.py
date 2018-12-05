from django.conf import settings
from django.contrib.gis.geos import Point

import factory

from geotrek.feedback import models as feedback_models


class ReportCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportCategory

    category = factory.Sequence(lambda n: u"Category %s" % n)


class ReportStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.ReportStatus

    status = factory.Sequence(lambda n: u"Status %s" % n)


class ReportFactory(factory.DjangoModelFactory):
    class Meta:
        model = feedback_models.Report

    name = factory.Sequence(lambda n: u"name %s" % n)
    email = factory.Sequence(lambda n: u"email%s@domain.tld" % n)
    comment = factory.Sequence(lambda n: u"comment %s" % n)
    geom = Point(700000, 6600000, srid=settings.SRID)
