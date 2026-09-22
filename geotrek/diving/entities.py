from django.conf import settings

from geotrek.common.mixins.entity_options import PublishableEntityOptions
from geotrek.diving.views import (
    DiveDocumentBookletPublic,
    DiveDocumentPublic,
    DiveMarkupPublic,
)


class DiveEntityOptions(PublishableEntityOptions):
    document_public_booklet_view = DiveDocumentBookletPublic
    document_public_view = DiveDocumentPublic
    markup_public_view = DiveMarkupPublic
    menu = settings.DIVE_MODEL_ENABLED
    layer = settings.DIVE_MODEL_ENABLED
