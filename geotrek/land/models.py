from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.core.models import Topology, Path
from geotrek.common.models import Organism
from geotrek.maintenance.models import Intervention, Project


class PhysicalType(StructureRelated):
    name = models.CharField(max_length=128, verbose_name=_(u"Name"), db_column='nom')

    class Meta:
        db_table = 'f_b_nature'
        verbose_name = _(u"Physical type")
        verbose_name_plural = _(u"Physical types")
        ordering = ['name']

    def __unicode__(self):
        return self.name


class PhysicalEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType, verbose_name=_(u"Physical type"),
                                      db_column='type')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_nature'
        verbose_name = _(u"Physical edge")
        verbose_name_plural = _(u"Physical edges")

    def __unicode__(self):
        return _(u"Physical edge") + u": %s" % self.physical_type

    @property
    def color_index(self):
        return self.physical_type_id

    @property
    def name(self):
        return self.physical_type_csv_display

    @property
    def physical_type_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.physical_type
        )

    @property
    def physical_type_csv_display(self):
        return unicode(self.physical_type)

    @classmethod
    def path_physicals(cls, path):
        return cls.objects.existing().select_related('physical_type').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_physicals(cls, topology):
        return cls.overlapping(topology).select_related('physical_type')


Path.add_property('physical_edges', PhysicalEdge.path_physicals, _(u"Physical edges"))
Topology.add_property('physical_edges', PhysicalEdge.topology_physicals, _(u"Physical edges"))
Intervention.add_property('physical_edges', lambda self: self.topology.physical_edges if self.topology else [], _(u"Physical edges"))
Project.add_property('physical_edges', lambda self: self.edges_by_attr('physical_edges'), _(u"Physical edges"))


class LandType(StructureRelated):
    name = models.CharField(max_length=128, db_column='foncier', verbose_name=_(u"Name"))
    right_of_way = models.BooleanField(db_column='droit_de_passage', verbose_name=_(u"Right of way"))

    class Meta:
        db_table = 'f_b_foncier'
        verbose_name = _(u"Land type")
        verbose_name_plural = _(u"Land types")
        ordering = ['name']

    def __unicode__(self):
        return self.name


class LandEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    land_type = models.ForeignKey(LandType, verbose_name=_(u"Land type"), db_column='type')
    owner = models.TextField(verbose_name=_(u"Owner"), db_column='proprietaire', blank=True)
    agreement = models.BooleanField(verbose_name=_(u"Agreement"), db_column='convention', default=False)

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_foncier'
        verbose_name = _(u"Land edge")
        verbose_name_plural = _(u"Land edges")

    def __unicode__(self):
        return _(u"Land edge") + u": %s" % self.land_type

    @property
    def color_index(self):
        return self.land_type_id

    @property
    def name(self):
        return self.land_type_csv_display

    @property
    def land_type_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.land_type
        )

    @property
    def land_type_csv_display(self):
        return unicode(self.land_type)

    @classmethod
    def path_lands(cls, path):
        return cls.objects.existing().select_related('land_type').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_lands(cls, topology):
        return cls.overlapping(topology).select_related('land_type')


Path.add_property('land_edges', LandEdge.path_lands, _(u"Land edges"))
Topology.add_property('land_edges', LandEdge.topology_lands, _(u"Land edges"))
Intervention.add_property('land_edges', lambda self: self.topology.land_edges if self.topology else [], _(u"Land edges"))
Project.add_property('land_edges', lambda self: self.edges_by_attr('land_edges'), _(u"Land edges"))


class CompetenceEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_competence'
        verbose_name = _(u"Competence edge")
        verbose_name_plural = _(u"Competence edges")

    def __unicode__(self):
        return _(u"Competence edge") + u": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @classmethod
    def path_competences(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_competences(cls, topology):
        return cls.overlapping(Topology.objects.get(pk=topology.pk)).select_related('organization')


Path.add_property('competence_edges', CompetenceEdge.path_competences, _(u"Competence edges"))
Topology.add_property('competence_edges', CompetenceEdge.topology_competences, _(u"Competence edges"))
Intervention.add_property('competence_edges', lambda self: self.topology.competence_edges if self.topology else [], _(u"Competence edges"))
Project.add_property('competence_edges', lambda self: self.edges_by_attr('competence_edges'), _(u"Competence edges"))


class WorkManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_travaux'
        verbose_name = _(u"Work management edge")
        verbose_name_plural = _(u"Work management edges")

    def __unicode__(self):
        return _(u"Work management edge") + u": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @classmethod
    def path_works(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_works(cls, topology):
        return cls.overlapping(topology).select_related('organization')


Path.add_property('work_edges', WorkManagementEdge.path_works, _(u"Work management edges"))
Topology.add_property('work_edges', WorkManagementEdge.topology_works, _(u"Work management edges"))
Intervention.add_property('work_edges', lambda self: self.topology.work_edges if self.topology else [], _(u"Work management edges"))
Project.add_property('work_edges', lambda self: self.edges_by_attr('work_edges'), _(u"Work management edges"))


class SignageManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_signaletique'
        verbose_name = _(u"Signage management edge")
        verbose_name_plural = _(u"Signage management edges")

    def __unicode__(self):
        return _(u"Signage management edge") + u": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @classmethod
    def path_signages(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_signages(cls, topology):
        return cls.overlapping(topology).select_related('organization')


Path.add_property('signage_edges', SignageManagementEdge.path_signages, _(u"Signage management edges"))
Topology.add_property('signage_edges', SignageManagementEdge.topology_signages, _(u"Signage management edges"))
Intervention.add_property('signage_edges', lambda self: self.topology.signage_edges if self.topology else [], _(u"Signage management edges"))
Project.add_property('signage_edges', lambda self: self.edges_by_attr('signage_edges'), _(u"Signage management edges"))
