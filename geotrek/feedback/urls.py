from django.conf import settings
from django.urls import path
from mapentity.registry import registry

from geotrek.feedback import models as feedback_models

from .views import CategoryList


app_name = 'feedback'
urlpatterns = [
    path('api/<str:lang>/feedback/categories.json', CategoryList.as_view(), name="categories_json"),
]

urlpatterns += registry.register(feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED)
