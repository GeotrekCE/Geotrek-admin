from django.conf import settings
from geotrek.common.urls import PublishableEntityOptions
from geotrek.outdoor import models as outdoor_models
from geotrek.outdoor import views as outdoor_views  # noqa Fix an import loop
from mapentity.registry import registry


app_name = 'outdoor'
urlpatterns = []


class SiteEntityOptions(PublishableEntityOptions):
    document_public_view = outdoor_views.SiteDocumentPublic
    markup_public_view = outdoor_views.SiteMarkupPublic


urlpatterns += registry.register(outdoor_models.Site, SiteEntityOptions,
                                 menu=settings.SITE_MODEL_ENABLED)
