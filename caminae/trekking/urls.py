from django.conf.urls import patterns

from .views import (
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList
)

from caminae.mapentity.urlizor import view_classes_to_url


urlpatterns = patterns('', *view_classes_to_url(
    TrekLayer, TrekList, TrekDetail, TrekCreate,
    TrekUpdate, TrekDelete, TrekJsonList
))
