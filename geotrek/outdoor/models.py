from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from geotrek.authent.models import StructureRelated
from geotrek.common.mixins import NoDeleteMixin, TimeStampedModelMixin, AddPropertyMixin
from mapentity.models import MapEntityMixin


class Site(AddPropertyMixin, MapEntityMixin, StructureRelated,
           TimeStampedModelMixin, NoDeleteMixin):
    geom = models.GeometryField(verbose_name=_("Location"), srid=settings.SRID)
    name = models.CharField(verbose_name=_("Name"), max_length=128)
    description = models.TextField(verbose_name=_("Description"), blank=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ('name', )

    def __str__(self):
        return self.name

    @property
    def name_display(self):
        return '<a data-pk="{pk}" href="{url}" title="{name}">{name}</a>'.format(
            pk=self.pk,
            url=self.get_detail_url(),
            name=self.name
        )
