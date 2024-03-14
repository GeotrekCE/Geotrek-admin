from django.urls import path, include, register_converter
from rest_framework.routers import DefaultRouter

from geotrek.flatpages.views import FlatPageViewSet
from geotrek.common.urls import LangConverter


"""
We don't use MapEntity for FlatPages, thus we use Django Rest Framework
without sugar.
"""
router = DefaultRouter(trailing_slash=False)
router.register('flatpages', FlatPageViewSet, basename='flatpages')

register_converter(LangConverter, 'lang')

app_name = 'flatpages'
urlpatterns = [
    path('api/<lang:lang>/', include(router.urls)),
]
