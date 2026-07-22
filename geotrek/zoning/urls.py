from django.conf import settings
from mapentity.registry import registry
from rest_framework.routers import DefaultRouter

from . import models, views

app_name = "zoning"

router = DefaultRouter()
router.register(r"api/city/city", views.CityViewSet, basename="city")
router.register(r"api/district/district", views.DistrictViewSet, basename="district")
router.register(
    r"api/restrictedarea/restrictedarea",
    views.RestrictedAreaViewSet,
    basename="restrictedarea",
)
router.register(
    r"api/restrictedarea/type/(?P<type_pk>[0-9]+)/restrictedarea",
    views.RestrictedAreaViewSet,
    basename="restrictedarea-by-type",
)

urlpatterns = []

urlpatterns += router.urls
urlpatterns += registry.register(
    models.VigilanceArea, menu=settings.VIGILANCE_AREA_MODEL_ENABLED
)
