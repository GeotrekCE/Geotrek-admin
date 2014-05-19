from django.conf import settings
from django.contrib.gis.geos import Point

import factory

from geotrek.feedback import models as feedback_models


class ReportCategoryFactory(factory.Factory):
    FACTORY_FOR = feedback_models.ReportCategory

    category = factory.Sequence(lambda n: u"Category %s" % n)


class ReportFactory(factory.Factory):
    FACTORY_FOR = feedback_models.Report

    name = factory.Sequence(lambda n: u"name %s" % n)
    email = factory.Sequence(lambda n: u"email%s@domain.tld" % n)
    comment = factory.Sequence(lambda n: u"comment %s" % n)
    geom = Point(2.26, 1.13, srid=settings.SRID)
