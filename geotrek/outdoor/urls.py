from django.conf import settings
from mapentity.registry import registry

from geotrek.common.urls import PublishableEntityOptions
from geotrek.outdoor import models as outdoor_models
from geotrek.outdoor import views as outdoor_views  # noqa Fix an import loop

app_name = "outdoor"

urlpatterns = []


class SiteEntityOptions(PublishableEntityOptions):
    document_public_view = outdoor_views.SiteDocumentPublic
    document_public_booklet_view = outdoor_views.SiteDocumentBookletPublic
    markup_public_view = outdoor_views.SiteMarkupPublic


class CourseEntityOptions(PublishableEntityOptions):
    document_public_view = outdoor_views.CourseDocumentPublic
    document_public_booklet_view = outdoor_views.CourseDocumentBookletPublic
    markup_public_view = outdoor_views.CourseMarkupPublic


urlpatterns += registry.register(
    outdoor_models.Site, SiteEntityOptions, menu=settings.SITE_MODEL_ENABLED
)
urlpatterns += registry.register(
    outdoor_models.Course, CourseEntityOptions, menu=settings.COURSE_MODEL_ENABLED
)
