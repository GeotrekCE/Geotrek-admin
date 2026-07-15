from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.api.v2.views.feedback import ReportViewSet
from geotrek.common.urls import LangConverter
from geotrek.feedback import models as feedback_models
from geotrek.feedback import views

register_converter(LangConverter, "lang")

app_name = "feedback"

urlpatterns = [
    # backward compatible report endpoint
    path(
        "api/<lang:lang>/reports/report",
        ReportViewSet.as_view({"post": "create"}),
        name="report",
    ),
    path(
        "api/report/references/",
        views.ReportReferences.as_view(),
        name="report_references",
    ),
]

urlpatterns += registry.register(
    feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED
)
