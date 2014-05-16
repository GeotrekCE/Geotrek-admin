import factory

from geotrek.feedback import models as feedback_models


class ReportFactory(factory.Factory):
    FACTORY_FOR = feedback_models.Report
