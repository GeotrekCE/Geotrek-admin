from django.conf.urls import patterns

from .views import (
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList
)

from caminae.core.entity import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList
))
