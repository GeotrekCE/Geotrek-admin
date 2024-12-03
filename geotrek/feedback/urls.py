from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter
from geotrek.feedback import models as feedback_models

from geotrek.api.v2.views.feedback import ReportViewSet

register_converter(LangConverter, 'lang')

app_name = 'feedback'

urlpatterns = [
    # backward compatible report endpoint
    path('api/<lang:lang>/reports/report', ReportViewSet.as_view({"post": "create"}), name="report"),
]

urlpatterns += registry.register(feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED)
