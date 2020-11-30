from django.conf import settings
from geotrek.outdoor import models as outdoor_models
from mapentity.registry import registry, MapEntityOptions


app_name = 'outdoor'
urlpatterns = []


class SiteEntityOptions(MapEntityOptions):
    pass


urlpatterns += registry.register(outdoor_models.Site, SiteEntityOptions,
                                 menu=settings.SITE_MODEL_ENABLED)
