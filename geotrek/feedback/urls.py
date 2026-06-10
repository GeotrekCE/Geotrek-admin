from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.api.v2.views.feedback import ReportViewSet
from geotrek.common.urls import LangConverter

from . import entities, models

register_converter(LangConverter, "lang")

app_name = "feedback"

urlpatterns = [
    # backward compatible report endpoint
    path(
        "api/<lang:lang>/reports/report",
        ReportViewSet.as_view({"post": "create"}),
        name="report",
    ),
]

urlpatterns += registry.register(models.Report, options=entities.ReportOptions)
