from django.conf.urls import patterns, include, url, static
from rest_framework import routers
from geotrek.api.v2 import views as api_views


router = routers.SimpleRouter()
router.register(r'touristiccontent', api_views.TouristicContentViewSet)
router.register(r'trek', api_views.TrekViewSet)
#router.register(r'roaming', api_views.RoamingViewSet)
router.register(r'poi', api_views.POIViewSet)

urlpatterns = [
    #url(r'^forgot-password/$', ForgotPasswordFormView.as_view()),
]

urlpatterns += router.urls