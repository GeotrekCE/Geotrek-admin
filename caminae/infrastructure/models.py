from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels

from extended_choices import Choices

from caminae.core.models import Topology, Path
from caminae.mapentity.models import MapEntityMixin
from caminae.authent.models import StructureRelatedManager, StructureRelated



INFRASTRUCTURE_TYPES = Choices(
    ('BUILDING', 'A', _("Building")),
    ('FACILITY', 'E', _("Facility")),
    ('SIGNAGE',  'S', _("Signage")),
)


class InfrastructureTypeQuerySet(models.query.QuerySet):
    def for_infrastructures(self):
        return self.exclude(type__exact=INFRASTRUCTURE_TYPES.SIGNAGE)

    def for_signages(self):
        return self.filter(type__exact=INFRASTRUCTURE_TYPES.SIGNAGE)


class InfrastructureTypeManager(models.Manager):
    def get_query_set(self):
        return InfrastructureTypeQuerySet(self.model, using=self._db)

    def for_signages(self):
        return self.get_query_set().for_signages()

    def for_infrastructures(self):
        return self.get_query_set().for_infrastructures()


class InfrastructureType(StructureRelated):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(db_column="nom", max_length=128)
    type = models.CharField(db_column="type", max_length=1, choices=INFRASTRUCTURE_TYPES)

    objects = InfrastructureTypeManager()

    class Meta:
        db_table = 'classe_amenagement'
        verbose_name = _(u"Infrastructure Type")
        verbose_name_plural = _(u"Infrastructure Types")

    def __unicode__(self):
        return self.label


class BaseInfrastructure(MapEntityMixin, Topology, StructureRelated):
    """ A generic infrastructure in the park """
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                      db_column='evenement')
    
    name = models.CharField(db_column="nom", max_length=128)
    description = models.TextField(blank=True)
    type = models.ForeignKey(InfrastructureType)

    class Meta:
        db_table = 'amenagement'
        verbose_name = _(u"Infrastructure")
        verbose_name_plural = _(u"Infrastructure")

    def __unicode__(self):
        return self.name

    @property
    def name_display(self):
        return '<a href="%s">%s</a>' % (self.get_detail_url(), self)

    @property
    def name_csv_display(self):
        return unicode(self)

    @property
    def type_display(self):
        return unicode(self.type)


class InfrastructureGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def get_query_set(self):
        return super(InfrastructureGISManager, self).get_query_set().exclude(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class InfrastructureStructureManager(StructureRelatedManager):
    """ Overide default structure related manager, and filter by type. """
    def get_query_set(self):
        return super(InfrastructureStructureManager, self).get_query_set().exclude(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class Infrastructure(BaseInfrastructure):
    """ An infrastructure in the park, which is not of type SIGNAGE """
    objects = BaseInfrastructure.get_manager_cls(InfrastructureGISManager)()
    in_structure = InfrastructureStructureManager()
    class Meta:
        proxy = True

    @classmethod
    def path_infrastructures(cls, path):
        return [Infrastructure.objects.get(pk=t.pk)
                for t in path.topology_set.existing().filter(
                    kind=Infrastructure.KIND)]

    Path.add_property('infrastructures', lambda self: Infrastructure.path_infrastructures(self))


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
    objects = BaseInfrastructure.get_manager_cls(SignageGISManager)()
    in_structure = SignageStructureManager()
    class Meta:
        proxy = True

    @classmethod
    def path_signages(cls, path):
        return [Signage.objects.get(pk=t.pk)
                for t in path.topology_set.existing().filter(
                    kind=Signage.KIND)]

Path.add_property('signages', lambda self: Signage.path_signages(self))
