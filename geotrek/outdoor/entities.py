from django.conf import settings

from geotrek.common.mixins.entity_options import PublishableEntityOptions
from geotrek.outdoor import views as outdoor_views


class SiteEntityOptions(PublishableEntityOptions):
    document_public_view = outdoor_views.SiteDocumentPublic
    document_public_booklet_view = outdoor_views.SiteDocumentBookletPublic
    markup_public_view = outdoor_views.SiteMarkupPublic
    menu = settings.SITE_MODEL_ENABLED
    layer = settings.SITE_MODEL_ENABLED


class CourseEntityOptions(PublishableEntityOptions):
    document_public_view = outdoor_views.CourseDocumentPublic
    document_public_booklet_view = outdoor_views.CourseDocumentBookletPublic
    markup_public_view = outdoor_views.CourseMarkupPublic
    menu = settings.COURSE_MODEL_ENABLED
    layer = settings.COURSE_MODEL_ENABLED
