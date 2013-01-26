from operator import attrgetter

from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from caminae.mapentity.models import MapEntityMixin
from caminae.authent.models import StructureRelated
from caminae.core.models import Topology, Path
from caminae.common.models import Organism
from caminae.maintenance.models import Intervention, Project


def topology_edges(topology, pathattr):
    s = []
    for p in topology.paths.all():
        s += getattr(p, pathattr)
    return list(set(s))


def project_edges(project, pathattr):
    s = []
    for i in project.interventions.all():
        s += getattr(i, pathattr)
    return list(set(s))


# Physical nature of paths

class PhysicalType(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Name"))

    class Meta:
        db_table = 'f_b_nature'
        verbose_name = _(u"Physical type")
        verbose_name_plural = _(u"Physical types")

    def __unicode__(self):
        return self.name


class PhysicalEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType, verbose_name=_(u"Physical type"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_nature'
        verbose_name = _(u"Physical edge")
        verbose_name_plural = _(u"Physical edges")

    def __unicode__(self):
        return _(u"Physical edge") + u": %s" % self.physical_type

    @property
    def physical_type_display(self):
        return self.display

    @property
    def physical_type_csv_display(self):
        return unicode(self.physical_type)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.physical_type)

    @classmethod
    def path_physicals(self, path):
        return list(set([PhysicalEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=PhysicalEdge.KIND)]))

    @classmethod
    def topology_physicals(cls, topology):
        s = []
        for p in topology.paths.all():
            s += p.physical_edges
        return list(set(s))

Path.add_property('physical_edges', lambda self: PhysicalEdge.path_physicals(self))
Topology.add_property('physical_edges', lambda self: topology_edges(self, 'physical_edges'))
Intervention.add_property('physical_edges', lambda self: self.topology.physical_edges if self.topology else [])
Project.add_property('physical_edges', lambda self: project_edges(self, 'physical_edges'))

# Type of land under paths

class LandType(StructureRelated):
    name = models.CharField(max_length=128, db_column='foncier', verbose_name=_(u"Name"))
    right_of_way = models.BooleanField(db_column='droit_de_passage', verbose_name=_(u"Right of way"))

    class Meta:
        db_table = 'f_b_foncier'
        verbose_name = _(u"Land type")
        verbose_name_plural = _(u"Land types")

    def __unicode__(self):
        return self.name


class LandEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    land_type = models.ForeignKey(LandType, verbose_name=_(u"Land type"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_foncier'
        verbose_name = _(u"Land edge")
        verbose_name_plural = _(u"Land edges")

    def __unicode__(self):
        return _(u"Land edge") + u": %s" % self.land_type

    @property
    def land_type_display(self):
        return self.display

    @property
    def land_type_csv_display(self):
        return unicode(self.land_type)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.land_type)

    @classmethod
    def path_lands(self, path):
        return list(set([LandEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=LandEdge.KIND)]))

Path.add_property('land_edges', lambda self: LandEdge.path_lands(self))
Topology.add_property('land_edges', lambda self: topology_edges(self, 'land_edges'))
Intervention.add_property('land_edges', lambda self: self.topology.land_edges if self.topology else [])
Project.add_property('land_edges', lambda self: project_edges(self, 'land_edges'))

# Interaction with external structures

class CompetenceEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_competence'
        verbose_name = _(u"Competence edge")
        verbose_name_plural = _(u"Competence edges")

    def __unicode__(self):
        return _(u"Competence edge") + u": %s" % self.organization

    @property
    def organization_display(self):
        return self.display

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.organization)

    @classmethod
    def path_competences(self, path):
        return list(set([CompetenceEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=CompetenceEdge.KIND)]))

Path.add_property('competence_edges', lambda self: CompetenceEdge.path_competences(self))
Topology.add_property('competence_edges', lambda self: topology_edges(self, 'competence_edges'))
Intervention.add_property('competence_edges', lambda self: self.topology.competence_edges if self.topology else [])
Project.add_property('competence_edges', lambda self: project_edges(self, 'competence_edges'))


class WorkManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_travaux'
        verbose_name = _(u"Work management edge")
        verbose_name_plural = _(u"Work management edges")

    def __unicode__(self):
        return _(u"Work management edge") + u": %s" % self.organization

    @property
    def organization_display(self):
        return self.display

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.organization)

    @classmethod
    def path_works(self, path):
        return list(set([WorkManagementEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=WorkManagementEdge.KIND)]))

Path.add_property('work_edges', lambda self: WorkManagementEdge.path_works(self))
Topology.add_property('work_edges', lambda self: topology_edges(self, 'work_edges'))
Intervention.add_property('work_edges', lambda self: self.topology.work_edges if self.topology else [])
Project.add_property('work_edges', lambda self: project_edges(self, 'work_edges'))


class SignageManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_gestion_signaletique'
        verbose_name = _(u"Signage management edge")
        verbose_name_plural = _(u"Signage management edges")

    def __unicode__(self):
        return _(u"Signage management edge") + u": %s" % self.organization

    @property
    def organization_display(self):
        return self.display

    @property
    def organization_csv_display(self):
        return unicode(self.organization)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.organization)

    @classmethod
    def path_signages(self, path):
        return list(set([SignageManagementEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=SignageManagementEdge.KIND)]))

Path.add_property('signage_edges', lambda self: SignageManagementEdge.path_signages(self))
Topology.add_property('signage_edges', lambda self: topology_edges(self, 'signage_edges'))
Intervention.add_property('signage_edges', lambda self: self.topology.signage_edges if self.topology else [])
Project.add_property('signage_edges', lambda self: project_edges(self, 'signage_edges'))



"""

   Zoning
   (not MapEntity : just layers, on which intersections with objects is done in triggers)

"""

class RestrictedAreaType(models.Model):
    name = models.CharField(max_length=200, verbose_name=_(u"Name"))

    class Meta:
        db_table = 'f_b_zonage'
        verbose_name = _(u"Restricted area type")


class RestrictedArea(models.Model):
    name = models.CharField(max_length=250, db_column='zonage', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    area_type = models.ForeignKey(RestrictedAreaType, verbose_name=_(u"Restricted area"))

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        ordering = ['area_type', 'name',]
        db_table = 'l_zonage_reglementaire'
        verbose_name = _(u"Restricted area")
        verbose_name_plural = _(u"Restricted areas")

    def __unicode__(self):
        return "%s - %s" % (self.area_type.name, self.name)


class RestrictedAreaEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    restricted_area = models.ForeignKey(RestrictedArea, verbose_name=_(u"Restricted area"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_zonage'
        verbose_name = _(u"Restricted area edge")
        verbose_name_plural = _(u"Restricted area edges")

    def __unicode__(self):
        return _(u"Restricted area edge") + u": %s" % self.restricted_area

    @classmethod
    def path_area_edges(cls, path):
        return list(set([RestrictedAreaEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=RestrictedAreaEdge.KIND)]))

Path.add_property('area_edges', lambda self: RestrictedAreaEdge.path_area_edges(self))
Path.add_property('areas', lambda self: list(set(map(attrgetter('restricted_area'), self.area_edges))))
Topology.add_property('area_edges', lambda self: topology_edges(self, 'area_edges'))
Topology.add_property('areas', lambda self: list(set(map(attrgetter('restricted_area'), self.area_edges))))
Intervention.add_property('area_edges', lambda self: self.topology.area_edges if self.topology else [])
Intervention.add_property('areas', lambda self: self.topology.areas if self.topology else [])
Project.add_property('area_edges', lambda self: project_edges(self, 'area_edges'))
Project.add_property('areas', lambda self: list(set(map(attrgetter('restricted_area'), self.area_edges))))


class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6, db_column='insee')
    name = models.CharField(max_length=128, db_column='commune', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        db_table = 'l_commune'
        ordering = ['name', ]
        verbose_name = _(u"City")
        verbose_name_plural = _(u"Cities")

    def __unicode__(self):
        return self.name


class CityEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')

    city = models.ForeignKey(City, verbose_name=_(u"City"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_commune'
        verbose_name = _(u"City edge")
        verbose_name_plural = _(u"City edges")

    def __unicode__(self):
        return _("City edge") + u": %s" % self.city

    @classmethod
    def path_city_edges(self, path):
        return list(set([CityEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=CityEdge.KIND)]))

Path.add_property('city_edges', lambda self: CityEdge.path_city_edges(self))
Path.add_property('cities', lambda self: list(set(map(attrgetter('city'), self.city_edges))))
Topology.add_property('city_edges', lambda self: topology_edges(self, 'city_edges'))
Topology.add_property('cities', lambda self: list(set(map(attrgetter('city'), self.city_edges))))
Intervention.add_property('city_edges', lambda self: self.topology.city_edges if self.topology else [])
Intervention.add_property('cities', lambda self: self.topology.cities if self.topology else [])
Project.add_property('city_edges', lambda self: project_edges(self, 'city_edges'))
Project.add_property('cities', lambda self: list(set(map(attrgetter('city'), self.city_edges))))


class District(models.Model):
    name = models.CharField(max_length=128, db_column='secteur', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        db_table = 'l_secteur'
        ordering = ['name', ]
        verbose_name = _(u"District")
        verbose_name_plural = _(u"Districts")

    def __unicode__(self):
        return self.name


class DistrictEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    district = models.ForeignKey(District, verbose_name=_(u"District"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'f_t_secteur'
        verbose_name = _(u"District edge")
        verbose_name_plural = _(u"District edges")

    def __unicode__(self):
        return _(u"District edge") + u": %s" % self.district

    @classmethod
    def path_district_edges(self, path):
        return list(set([DistrictEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=DistrictEdge.KIND)]))

Path.add_property('district_edges', lambda self: DistrictEdge.path_district_edges(self))
Path.add_property('districts', lambda self: list(set(map(attrgetter('district'), self.district_edges))))
Topology.add_property('district_edges', lambda self: topology_edges(self, 'district_edges'))
Topology.add_property('districts', lambda self: list(set(map(attrgetter('district'), self.district_edges))))
Intervention.add_property('district_edges', lambda self: self.topology.district_edges if self.topology else [])
Intervention.add_property('districts', lambda self: self.topology.districts if self.topology else [])
Project.add_property('district_edges', lambda self: project_edges(self, 'district_edges'))
Project.add_property('districts', lambda self: list(set(map(attrgetter('district'), self.district_edges))))
