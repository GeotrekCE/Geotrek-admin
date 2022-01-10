from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.common.urls import LangConverter
from geotrek.feedback import models as feedback_models

from .views import (CategoryList, ClassifiedReportLayer, FeedbackOptionsView,
                    FiledReportLayer, LateInterventionReportLayer,
                    ProgrammedReportLayer, SolvedInterventionReportLayer, LateResolutionReportLayer,
                    SolvedReportLayer, WaitingReportLayer)

register_converter(LangConverter, 'lang')

app_name = 'feedback'
urlpatterns = [
    path('api/<lang:lang>/feedback/categories.json', CategoryList.as_view(), name="categories_json"),
    path('api/<lang:lang>/feedback/options.json', FeedbackOptionsView.as_view(), name="options_json"),
]

urlpatterns += registry.register(feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED)
urlpatterns += [
    path("api/report/report-waiting.geojson", WaitingReportLayer.as_view()),
    path("api/report/report-filed.geojson", FiledReportLayer.as_view()),
    path("api/report/report-intervention_late.geojson", LateInterventionReportLayer.as_view()),
    path("api/report/report-intervention_solved.geojson", SolvedInterventionReportLayer.as_view()),
    path("api/report/report-classified.geojson", ClassifiedReportLayer.as_view()),
    path("api/report/report-resolved.geojson", SolvedReportLayer.as_view()),
    path("api/report/report-resolution_late.geojson", LateResolutionReportLayer.as_view()),
    path("api/report/report-programmed.geojson", ProgrammedReportLayer.as_view()),
]
