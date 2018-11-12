from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels

from extended_choices import Choices
from mapentity.models import MapEntityMixin

from geotrek.common.utils import classproperty
from geotrek.core.models import Topology, Path
from geotrek.authent.models import StructureRelatedManager, StructureRelated, StructureOrNoneRelated
from geotrek.common.mixins import BasePublishableMixin, PictogramMixin


INFRASTRUCTURE_TYPES = Choices(
    ('BUILDING', 'A', _("Building")),
    ('FACILITY', 'E', _("Facility")),
    ('SIGNAGE', 'S', _("Signage")),
)


class InfrastructureTypeQuerySet(models.query.QuerySet):
    def for_infrastructures(self):
        return self.exclude(type__exact=INFRASTRUCTURE_TYPES.SIGNAGE)

    def for_signages(self):
        return self.filter(type__exact=INFRASTRUCTURE_TYPES.SIGNAGE)


class InfrastructureTypeManager(models.Manager):
    def get_queryset(self):
        return InfrastructureTypeQuerySet(self.model, using=self._db)

    def for_signages(self):
        return self.get_queryset().for_signages()

    def for_infrastructures(self):
        return self.get_queryset().for_infrastructures()


class InfrastructureType(StructureOrNoneRelated, PictogramMixin):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(db_column="nom", max_length=128)
    type = models.CharField(db_column="type", max_length=1, choices=INFRASTRUCTURE_TYPES)

    objects = InfrastructureTypeManager()

    class Meta:
        db_table = 'a_b_amenagement'
        verbose_name = _(u"Infrastructure Type")
        verbose_name_plural = _(u"Infrastructure Types")
        ordering = ['label', 'type']

    def __unicode__(self):
        if self.structure:
            return u"{} ({})".format(self.label, self.structure.name)
        return self.label


class InfrastructureCondition(StructureOrNoneRelated):
    label = models.CharField(verbose_name=_(u"Name"), db_column="etat", max_length=250)

    class Meta:
        verbose_name = _(u"Infrastructure Condition")
        verbose_name_plural = _(u"Infrastructure Conditions")
        db_table = "a_b_etat"

    def __unicode__(self):
        if self.structure:
            return u"{} ({})".format(self.label, self.structure.name)
        return self.label


class BaseInfrastructure(MapEntityMixin, BasePublishableMixin, Topology, StructureRelated):
    """ A generic infrastructure in the park """
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')

    name = models.CharField(db_column="nom", max_length=128,
                            help_text=_(u"Reference, code, ..."), verbose_name=_("Name"))
    description = models.TextField(blank=True, db_column='description',
                                   verbose_name=_("Description"), help_text=_(u"Specificites"))
    type = models.ForeignKey(InfrastructureType, db_column='type', verbose_name=_("Type"))
    condition = models.ForeignKey(InfrastructureCondition, db_column='etat',
                                  verbose_name=_("Condition"), blank=True, null=True,
                                  on_delete=models.PROTECT)
    implantation_year = models.PositiveSmallIntegerField(verbose_name=_("Implantation year"),
                                                         db_column='annee_implantation', null=True)

    class Meta:
        db_table = 'a_t_amenagement'

    def __unicode__(self):
        return self.name

    @property
    def implantation_year_display(self):
        return u"{}".format(self.implantation_year) if self.implantation_year else ""

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk, self.get_detail_url(),
                                                              self,
                                                              self)
        if self.published:
            s = u'<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        return s

    @property
    def name_csv_display(self):
        return unicode(self)

    @property
    def type_display(self):
        return unicode(self.type)

    @property
    def cities_display(self):
        if hasattr(self, 'cities'):
            return [unicode(c) for c in self.cities]
        return []

    @classproperty
    def cities_verbose_name(cls):
        return _("Cities")


class InfrastructureGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def get_queryset(self):
        return super(InfrastructureGISManager, self).get_queryset().exclude(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)

    def all_implantation_years(self):
        all_years = self.get_queryset().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').values_list('implantation_year', flat=True).distinct('implantation_year')
        return all_years


class InfrastructureStructureManager(StructureRelatedManager):
    """ Overide default structure related manager, and filter by type. """
    def get_queryset(self):
        return super(InfrastructureStructureManager, self).get_queryset().exclude(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class Infrastructure(BaseInfrastructure):
    """ An infrastructure in the park, which is not of type SIGNAGE """
    objects = BaseInfrastructure.get_manager_cls(InfrastructureGISManager)()
    in_structure = InfrastructureStructureManager()

    class Meta:
        proxy = True
        verbose_name = _(u"Infrastructure")
        verbose_name_plural = _(u"Infrastructures")

    @classmethod
    def path_infrastructures(cls, path):
        return cls.objects.existing().filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_infrastructures(cls, topology):
        return cls.overlapping(topology)

    @classmethod
    def published_topology_infrastructure(cls, topology):
        return cls.topology_infrastructures(topology).filter(published=True)


Path.add_property('infrastructures', lambda self: Infrastructure.path_infrastructures(self), _(u"Infrastructures"))
Topology.add_property('infrastructures', lambda self: Infrastructure.topology_infrastructures(self), _(u"Infrastructures"))
Topology.add_property('published_infrastructures', Infrastructure.published_topology_infrastructure,
                      _(u"Published Infrastructures"))


class SignageGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def get_queryset(self):
        return super(SignageGISManager, self).get_queryset().filter(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)

    def all_implantation_years(self):
        all_years = self.get_queryset().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').values_list('implantation_year', flat=True).distinct('implantation_year')
        return all_years


class SignageStructureManager(StructureRelatedManager):
    """ Overide default structure related manager, and filter by type. """
    def get_queryset(self):
        return super(SignageStructureManager, self).get_queryset().filter(type__type=INFRASTRUCTURE_TYPES.SIGNAGE)


class Signage(BaseInfrastructure):
    """ An infrastructure in the park, which is of type SIGNAGE """
    objects = BaseInfrastructure.get_manager_cls(SignageGISManager)()
    in_structure = SignageStructureManager()

    class Meta:
        proxy = True
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
