from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import ugettext_lazy as _
from mapentity.models import MapEntityMixin

from geotrek.common.models import TimeStampedModel


class Report(MapEntityMixin, TimeStampedModel):
    """ User reports, mainly submitted via *Geotrek-rando*.
    """
    name = models.CharField(verbose_name=_(u"Name"), max_length=256)
    email = models.EmailField(verbose_name=_(u"Email"))
    comment = models.TextField(blank=True,
                               default="",
                               verbose_name=_(u"Comment"))
    geom = gis_models.PointField(null=True,
                                 default=None,
                                 verbose_name=_(u"Location"),
                                 srid=settings.SRID)

    objects = gis_models.GeoManager()
