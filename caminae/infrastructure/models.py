from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels

from extended_choices import Choices

from caminae.core.models import TopologyMixin
from caminae.authent.models import StructureRelatedManager, StructureRelated


INFRASTRUCTURE_TYPES = Choices(
    ('BUILDING', 'A', _("Building")),
    ('FACILITY', 'E', _("Facility")),
    ('SIGNAGE',  'S', _("Signage")),
)


class InfrastructureType(StructureRelated):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(db_column="nom", max_length=128)
    type = models.CharField(db_column="type", max_length=1, choices=INFRASTRUCTURE_TYPES)

    class Meta:
        db_table = 'classe_amenagement'
        verbose_name = _(u"Infrastructure Type")
        verbose_name_plural = _(u"Infrastructure Types")

    def __unicode__(self):
        return self.label


class BaseInfrastructure(TopologyMixin, StructureRelated):
    """ A generic infrastructure in the park """
    name = models.CharField(db_column="nom", max_length=128)
    description = models.TextField(blank=True)
    type = models.ForeignKey(InfrastructureType)

    class Meta:
        db_table = 'amenagement'
        verbose_name = _(u"Infrastructure")
        verbose_name_plural = _(u"Infrastructure")

    def __unicode__(self):
        return self.name


class InfrastructureGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def get_query_set(self):
        return super(InfrastructureGISManager, self).get_query_set().filter(type__type__ne=INFRASTRUCTURE_TYPES.SIGNAGE)


class InfrastructureStructureManager(StructureRelatedManager):
    """ Overide default structure related manager, and filter by type. """
    def get_query_set(self):
        return super(InfrastructureStructureManager, self).get_query_set().filter(type__type__ne=INFRASTRUCTURE_TYPES.SIGNAGE)


class Infrastructure(BaseInfrastructure):
    """ An infrastructure in the park, which is not of type SIGNAGE """
    objects = InfrastructureGISManager()
    in_structure = InfrastructureStructureManager()
    class Meta:
        proxy = True


class SignageGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def get_query_set(self):
        return super(SignageGISManager, self).get_query_set().filter(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class SignageStructureManager(StructureRelatedManager):
    """ Overide default structure related manager, and filter by type. """
    def get_query_set(self):
        return super(SignageStructureManager, self).get_query_set().filter(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class Signage(BaseInfrastructure):
    """ An infrastructure in the park, which is of type SIGNAGE """
    objects = SignageGISManager()
    in_structure = SignageStructureManager()
    class Meta:
        proxy = True
