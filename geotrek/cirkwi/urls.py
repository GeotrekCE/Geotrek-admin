from django.urls import path

from geotrek.cirkwi.views import CirkwiPOIView, CirkwiTrekView

urlpatterns = [
    path("api/cirkwi/circuits.xml", CirkwiTrekView.as_view()),
    path("api/cirkwi/pois.xml", CirkwiPOIView.as_view()),
]
