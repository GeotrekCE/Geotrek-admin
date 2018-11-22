from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureOrNoneRelated
from geotrek.core.models import Topology, Path
from geotrek.common.models import Organism
from geotrek.maintenance.models import Intervention, Project


class PhysicalType(StructureOrNoneRelated):
    name = models.CharField(max_length=128, verbose_name=_("Name"), db_column='nom')

    class Meta:
        db_table = 'f_b_nature'
        verbose_name = _("Physical type")
        verbose_name_plural = _("Physical types")
        ordering = ['name']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.name, self.structure.name)
        return self.name


class PhysicalEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType, verbose_name=_("Physical type"),
                                      db_column='type')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_nature'
        verbose_name = _("Physical edge")
        verbose_name_plural = _("Physical edges")

    def __str__(self):
        return _("Physical edge") + ": %s" % self.physical_type

    @property
    def color_index(self):
        return self.physical_type_id

    @property
    def name(self):
        return self.physical_type_csv_display

    @property
    def physical_type_display(self):
        return '<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.physical_type
        )

    @property
    def physical_type_csv_display(self):
        return str(self.physical_type)

    @classmethod
    def path_physicals(cls, path):
        return cls.objects.existing().select_related('physical_type').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_physicals(cls, topology):
        return cls.overlapping(topology).select_related('physical_type')


Path.add_property('physical_edges', PhysicalEdge.path_physicals, _("Physical edges"))
Topology.add_property('physical_edges', PhysicalEdge.topology_physicals, _("Physical edges"))
Intervention.add_property(
    'physical_edges', lambda self: self.topology.physical_edges if self.topology else [], _("Physical edges")
)
Project.add_property('physical_edges', lambda self: self.edges_by_attr('physical_edges'), _("Physical edges"))


class LandType(StructureOrNoneRelated):
    name = models.CharField(max_length=128, db_column='foncier', verbose_name=_("Name"))
    right_of_way = models.BooleanField(default=False, db_column='droit_de_passage', verbose_name=_("Right of way"))

    class Meta:
        db_table = 'f_b_foncier'
        verbose_name = _("Land type")
        verbose_name_plural = _("Land types")
        ordering = ['name']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.name, self.structure.name)
        return self.name


class LandEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    land_type = models.ForeignKey(LandType, verbose_name=_("Land type"), db_column='type')
    owner = models.TextField(verbose_name=_("Owner"), db_column='proprietaire', blank=True)
    agreement = models.BooleanField(verbose_name=_("Agreement"), db_column='convention', default=False)

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_foncier'
        verbose_name = _("Land edge")
        verbose_name_plural = _("Land edges")

    def __str__(self):
        return _("Land edge") + ": %s" % self.land_type

    @property
    def color_index(self):
        return self.land_type_id

    @property
    def name(self):
        return self.land_type_csv_display

    @property
    def land_type_display(self):
        return '<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.land_type
        )

    @property
    def land_type_csv_display(self):
        return str(self.land_type)

    @classmethod
    def path_lands(cls, path):
        return cls.objects.existing().select_related('land_type').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_lands(cls, topology):
        return cls.overlapping(topology).select_related('land_type')


Path.add_property('land_edges', LandEdge.path_lands, _("Land edges"))
Topology.add_property('land_edges', LandEdge.topology_lands, _("Land edges"))
Intervention.add_property('land_edges', lambda self: self.topology.land_edges if self.topology else [], _("Land edges"))
Project.add_property('land_edges', lambda self: self.edges_by_attr('land_edges'), _("Land edges"))


class CompetenceEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_("Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_competence'
        verbose_name = _("Competence edge")
        verbose_name_plural = _("Competence edges")

    def __str__(self):
        return _("Competence edge") + ": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return '<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return str(self.organization)

    @classmethod
    def path_competences(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_competences(cls, topology):
        return cls.overlapping(Topology.objects.get(pk=topology.pk)).select_related('organization')


Path.add_property('competence_edges', CompetenceEdge.path_competences, _("Competence edges"))
Topology.add_property('competence_edges', CompetenceEdge.topology_competences, _("Competence edges"))
Intervention.add_property(
    'competence_edges', lambda self: self.topology.competence_edges if self.topology else [], _("Competence edges")
)
Project.add_property('competence_edges', lambda self: self.edges_by_attr('competence_edges'), _("Competence edges"))


class WorkManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_("Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_travaux'
        verbose_name = _("Work management edge")
        verbose_name_plural = _("Work management edges")

    def __str__(self):
        return _("Work management edge") + ": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return '<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return str(self.organization)

    @classmethod
    def path_works(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_works(cls, topology):
        return cls.overlapping(topology).select_related('organization')


Path.add_property('work_edges', WorkManagementEdge.path_works, _("Work management edges"))
Topology.add_property('work_edges', WorkManagementEdge.topology_works, _("Work management edges"))
Intervention.add_property(
    'work_edges', lambda self: self.topology.work_edges if self.topology else [], _("Work management edges")
)
Project.add_property('work_edges', lambda self: self.edges_by_attr('work_edges'), _("Work management edges"))


class SignageManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_("Organism"), db_column='organisme')

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_signaletique'
        verbose_name = _("Signage management edge")
        verbose_name_plural = _("Signage management edges")

    def __str__(self):
        return _("Signage management edge") + ": %s" % self.organization

    @property
    def color_index(self):
        return self.organization_id

    @property
    def name(self):
        return self.organization_csv_display

    @property
    def organization_display(self):
        return '<a data-pk="%s" href="%s" >%s</a>' % (
            self.pk,
            self.get_detail_url(),
            self.organization
        )

    @property
    def organization_csv_display(self):
        return str(self.organization)

    @classmethod
    def path_signages(cls, path):
        return cls.objects.existing().select_related('organization').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_signages(cls, topology):
        return cls.overlapping(topology).select_related('organization')


Path.add_property('signage_edges', SignageManagementEdge.path_signages, _("Signage management edges"))
Topology.add_property('signage_edges', SignageManagementEdge.topology_signages, _("Signage management edges"))
Intervention.add_property(
    'signage_edges', lambda self: self.topology.signage_edges if self.topology else [], _("Signage management edges")
)
Project.add_property('signage_edges', lambda self: self.edges_by_attr('signage_edges'), _("Signage management edges"))
