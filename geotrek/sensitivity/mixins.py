import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F, Case, When, Prefetch
from geotrek.common.models import Attachment
from geotrek.common.functions import GeometryType, Buffer, Area

logger = logging.getLogger(__name__)

class SensitiveAreaQueryset:
    """Mixin used for to properly querying SensitiveAreas"""

    def get_queryset(self, *args, **kwargs):
        qs = super(SensitiveAreaQueryset, self).get_queryset()
        qs = (
            (
                qs
                .filter(published=True)
                .select_related("species", "structure")
                .prefetch_related(
                    "species__practices",
                    Prefetch(
                        "attachments",
                        queryset=Attachment.objects.select_related(
                            "license", "filetype", "filetype__structure"
                        ),
                    ),
                )
            )
            .annotate(geom_type=GeometryType(F("geom")))
            .annotate(
                geom2d_transformed=Case(
                    When(
                        geom_type="POINT",
                        then=Transform(
                            Buffer(F("geom"), F("species__radius"), 4),
                            settings.API_SRID,
                        ),
                    ),
                    When(
                        geom_type__in=("POLYGON", "MULTIPOLYGON"),
                        then=Transform(F("geom"), settings.API_SRID),
                    ),
                )
            )
            .annotate(area=Area("geom2d_transformed"))
            .order_by("-area")
            )

        if "practices" in self.request.GET:
            qs = qs.filter(
                species__practices__name__in=self.request.GET["practices"].split(",")
            )

        return qs
