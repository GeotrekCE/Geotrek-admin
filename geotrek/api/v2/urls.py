from django.conf.urls import patterns, include, url, static
from rest_framework import routers
from geotrek.api.v2 import views as api_views


router = routers.SimpleRouter()
router.register(r'touristiccontent', api_views.TouristicContentViewSet)
router.register(r'itinerance', api_views.ItineranceViewSet)

urlpatterns = [
    #url(r'^forgot-password/$', ForgotPasswordFormView.as_view()),
]

urlpatterns += router.urls