import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels
from django.conf import settings

from mapentity.models import MapEntityMixin

from geotrek.core.models import Topology, Path
from geotrek.authent.models import StructureOrNoneRelated
from geotrek.common.mixins import OptionalPictogramMixin
from geotrek.common.models import Organism
from geotrek.infrastructure.models import BaseInfrastructure


class SignageSealing(StructureOrNoneRelated):
    """ A sealing linked with a signage"""
    label = models.CharField(verbose_name=_(u"Name"), db_column="etat", max_length=250)

    class Meta:
        db_table = 'a_b_scellement'
        verbose_name = _(u"Signage Sealing")
        verbose_name_plural = _(u"Signages Sealing")

    def __unicode__(self):
        if self.structure:
            return u"{} ({})".format(self.label, self.structure.name)
        return self.label


class SignageType(StructureOrNoneRelated, OptionalPictogramMixin):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(db_column="nom", max_length=128)

    class Meta:
        db_table = 'a_b_signaletique'
        verbose_name = _(u"Signage Type")
        verbose_name_plural = _(u"Signage Types")

    def __unicode__(self):
        if self.structure:
            return u"{} ({})".format(self.label, self.structure.name)
        return self.label

    def get_pictogram_url(self):
        pictogram_url = super(SignageType, self).get_pictogram_url()
        if pictogram_url:
            return pictogram_url
        return os.path.join(settings.STATIC_URL, 'infrastructure/picto-signage.png')


class SignageGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def all_implantation_years(self):
        all_years = self.get_queryset().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').values_list('implantation_year', flat=True).distinct('implantation_year')
        return all_years


class Signage(MapEntityMixin, BaseInfrastructure):
    """ An infrastructure in the park, which is of type SIGNAGE """
    objects = BaseInfrastructure.get_manager_cls(SignageGISManager)()
    code = models.CharField(verbose_name=_(u"Code commune"), max_length=250, blank=True, null=True,
                            db_column='code_commune')
    administrator = models.ForeignKey(Organism, db_column='gestionnaire', verbose_name=_("Administrator"), null=True)
    sealing = models.ForeignKey(SignageSealing, db_column='scellement', verbose_name=_("Sealing"), null=True)
    printed_elevation = models.IntegerField(verbose_name=_(u"Printed Elevation"), blank=True, null=True,
                                            db_column='altitude_imprimee')
    type = models.ForeignKey(SignageType, db_column='type', verbose_name=_("Type"))

    class Meta:
        db_table = 'a_t_signaletique'
        verbose_name = _(u"Signage")
        verbose_name_plural = _(u"Signages")

    @classmethod
    def path_signages(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_signages(cls, topology):
        return cls.overlapping(topology)

    @classmethod
    def published_topology_signages(cls, topology):
        return cls.topology_signages(topology).filter(published=True)


Path.add_property('signages', lambda self: Signage.path_signages(self), _(u"Signages"))
Topology.add_property('signages', lambda self: Signage.topology_signages(self), _(u"Signages"))
Topology.add_property('published_signages', lambda self: Signage.published_topology_signages(self),
                      _(u"Published Signages"))
