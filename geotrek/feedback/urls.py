from django.conf.urls import patterns, url
from mapentity import registry

from geotrek.feedback import models as feedback_models

from .views import CategoryList


urlpatterns = patterns(
    '',
    url(r'^api/(?P<lang>\w+)/feedback/categories.json$', CategoryList.as_view(), name="categories_json"),
)

urlpatterns += registry.register(feedback_models.Report)
