import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models as gismodels
from django.conf import settings

from extended_choices import Choices
from mapentity.models import MapEntityMixin

from geotrek.common.utils import classproperty
from geotrek.core.models import Topology, Path
from geotrek.authent.models import StructureRelated, StructureOrNoneRelated
from geotrek.common.mixins import BasePublishableMixin, OptionalPictogramMixin


INFRASTRUCTURE_TYPES = Choices(
    ('BUILDING', 'A', _("Building")),
    ('FACILITY', 'E', _("Facility")),
    ('SIGNAGE', 'S', _("Signage")),
)


class InfrastructureType(StructureOrNoneRelated, OptionalPictogramMixin):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(db_column="nom", max_length=128)
    type = models.CharField(db_column="type", max_length=1, choices=INFRASTRUCTURE_TYPES)

    class Meta:
        db_table = 'a_b_amenagement'
        verbose_name = _(u"Infrastructure Type")
        verbose_name_plural = _(u"Infrastructure Types")
        ordering = ['label', 'type']

    def __unicode__(self):
        if self.structure:
            return u"{} ({})".format(self.label, self.structure.name)
        return self.label

    def get_pictogram_url(self):
        pictogram_url = super(InfrastructureType, self).get_pictogram_url()
        if pictogram_url:
            return pictogram_url
        return os.path.join(settings.STATIC_URL, 'infrastructure/picto-infrastructure.png')


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


class BaseInfrastructure(BasePublishableMixin, Topology, StructureRelated):
    """ A generic infrastructure in the park """
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')

    name = models.CharField(db_column="nom", max_length=128,
                            help_text=_(u"Reference, code, ..."), verbose_name=_("Name"))
    description = models.TextField(blank=True, db_column='description',
                                   verbose_name=_("Description"), help_text=_(u"Specificites"))
    condition = models.ForeignKey(InfrastructureCondition, db_column='etat',
                                  verbose_name=_("Condition"), blank=True, null=True,
                                  on_delete=models.PROTECT)
    implantation_year = models.PositiveSmallIntegerField(verbose_name=_("Implantation year"),
                                                         db_column='annee_implantation', null=True)
    eid = models.CharField(verbose_name=_(u"External id"), max_length=1024, blank=True, null=True,
                           db_column='id_externe')

    class Meta:
        abstract = True

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
        return [unicode(c) for c in self.cities] if hasattr(self, 'cities') else []

    @classproperty
    def cities_verbose_name(cls):
        return _("Cities")


class InfrastructureGISManager(gismodels.GeoManager):
    """ Overide default typology mixin manager, and filter by type. """
    def all_implantation_years(self):
        all_years = self.get_queryset().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').values_list('implantation_year', flat=True).distinct('implantation_year')
        return all_years


class Infrastructure(MapEntityMixin, BaseInfrastructure):
    """ An infrastructure in the park, which is not of type SIGNAGE """
    type = models.ForeignKey(InfrastructureType, db_column='type', verbose_name=_("Type"))
    objects = BaseInfrastructure.get_manager_cls(InfrastructureGISManager)()

    class Meta:
        db_table = 'a_t_infrastructure'
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
