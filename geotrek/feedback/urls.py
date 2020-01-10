from django.conf import settings
from django.urls import path, register_converter
from mapentity.registry import registry

from geotrek.feedback import models as feedback_models
from geotrek.common.urls import LangConverter

from .views import CategoryList

register_converter(LangConverter, 'lang')

app_name = 'feedback'
urlpatterns = [
    path('api/<lang:lang>/feedback/categories.json', CategoryList.as_view(), name="categories_json"),
]

urlpatterns += registry.register(feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED)
