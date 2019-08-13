from django.conf import settings
from django.conf.urls import url
from mapentity.registry import registry

from geotrek.feedback import models as feedback_models

from .views import CategoryList


urlpatterns = [
    url(r'^api/(?P<lang>\w+)/feedback/categories.json$', CategoryList.as_view(), name="categories_json"),
]

urlpatterns += registry.register(feedback_models.Report, menu=settings.REPORT_MODEL_ENABLED)
