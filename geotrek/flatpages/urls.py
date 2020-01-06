from django.urls import path, include
from rest_framework.routers import DefaultRouter

from geotrek.flatpages.views import FlatPageViewSet, FlatPageMeta


"""
We don't use MapEntity for FlatPages, thus we use Django Rest Framework
without sugar.
"""
router = DefaultRouter(trailing_slash=False)
router.register('flatpages', FlatPageViewSet, base_name='flatpages')

app_name = 'flatpages'
urlpatterns = [
    path('api/<str:lang>/', include(router.urls)),
    path('api/<str:lang>/flatpages/<int:pk>/meta.html', FlatPageMeta.as_view(), name="flatpage_meta"),
]
