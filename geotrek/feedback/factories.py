import factory

from geotrek.feedback import models as feedback_models


class ReportCategoryFactory(factory.Factory):
    FACTORY_FOR = feedback_models.ReportCategory


class ReportFactory(factory.Factory):
    FACTORY_FOR = feedback_models.Report

    category = factory.SubFactory(ReportCategoryFactory)
