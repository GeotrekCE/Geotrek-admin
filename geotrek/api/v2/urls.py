from django.conf.urls import patterns, include, url, static
from rest_framework import routers
from geotrek.api.v2 import views as api_views


router = routers.SimpleRouter()
router.register(r'touristiccontent', api_views.TouristicContentViewSet)
router.register(r'trek', api_views.TrekViewSet, base_name='trek')
router.register(r'roaming', api_views.RoamingViewSet, base_name='roaming')
router.register(r'poi', api_views.POIViewSet, base_name='poi')

urlpatterns = [
    #url(r'^forgot-password/$', ForgotPasswordFormView.as_view()),
]

urlpatterns += router.urls