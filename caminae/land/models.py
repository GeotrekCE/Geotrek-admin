from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from caminae.mapentity.models import MapEntityMixin
from caminae.authent.models import StructureRelated
from caminae.core.models import Topology, Path
from caminae.common.models import Organism


# Physcal nature of paths

class PhysicalType(models.Model):
    name = models.CharField(max_length=128, verbose_name=_(u"Name"))

    class Meta:
        db_table = 'nature_sentier'
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
        db_table = 'nature'
        verbose_name = _(u"Physical edge")
        verbose_name_plural = _(u"Physical edges")

    @property
    def physical_type_display(self):
        return unicode(self.physical_type)

    @property
    def display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.physical_type)

    @classmethod
    def path_physicals(self, path):
        return list(set([PhysicalEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=PhysicalEdge.KIND)]))

Path.add_property('physical_edges', lambda self: PhysicalEdge.path_physicals(self))


# Type of land under paths

class LandType(StructureRelated):
    name = models.CharField(max_length=128, db_column='foncier', verbose_name=_(u"Name"))
    right_of_way = models.BooleanField(db_column='droit_de_passage', verbose_name=_(u"Right of way"))

    class Meta:
        db_table = 'type_foncier'
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
        db_table = 'foncier'
        verbose_name = _(u"Land edge")
        verbose_name_plural = _(u"Land edges")

    @property
    def land_type_display(self):
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



# Interaction with external structures

class CompetenceEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'competence'
        verbose_name = _(u"Competence edge")
        verbose_name_plural = _(u"Competence edges")

    @property
    def organization_display(self):
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



class WorkManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'gestion_travaux'
        verbose_name = _(u"Work management edge")
        verbose_name_plural = _(u"Work management edges")

    @property
    def organization_display(self):
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



class SignageManagementEdge(MapEntityMixin, Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'gestion_signaletique'
        verbose_name = _(u"Signage management edge")
        verbose_name_plural = _(u"Signage management edges")

    @property
    def organization_display(self):
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


# Zoning

class RestrictedArea(models.Model):
    name = models.CharField(max_length=128, db_column='zonage', verbose_name=_(u"Name"))
    order = models.IntegerField(db_column='order', verbose_name=_(u"Order"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        db_table = 'couche_zonage_reglementaire'
        verbose_name = _(u"Restricted area")
        verbose_name_plural = _(u"Restricted areas")

    def __unicode__(self):
        return self.name


class RestrictedAreaEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       db_column='evenement')
    restricted_area = models.ForeignKey(RestrictedArea, verbose_name=_(u"Restricted area"))

    # Override default manager
    objects = Topology.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'zonage'
        verbose_name = _(u"Restricted area edge")
        verbose_name_plural = _(u"Restricted area edges")

    @property
    def display(self):
        return unicode(self)


    @classmethod
    def path_area_edges(cls, path):
        return list(set([RestrictedAreaEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=RestrictedAreaEdge.KIND)]))

    @classmethod
    def path_areas(cls, path):
        return [e.restricted_area for e in cls.path_area_edges(path)]

    @classmethod
    def topology_area_edges(cls, topology):
        s = []
        for p in topology.paths.all():
            s += p.area_edges
        return list(set(s))

    @classmethod
    def topology_areas(cls, topology):
        return [e.restricted_area for e in cls.topology_areas(topology)]

Path.add_property('area_edges', lambda self: RestrictedAreaEdge.path_area_edges(self))
Path.add_property('areas', lambda self: RestrictedAreaEdge.path_areas(self))
Topology.add_property('area_edges', lambda self: RestrictedAreaEdge.topology_area_edges(self))
Topology.add_property('areas', lambda self: RestrictedAreaEdge.topology_areas(self))


class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6, db_column='insee')
    name = models.CharField(max_length=128, db_column='commune', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        db_table = 'couche_communes'
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
        db_table = 'commune'
        verbose_name = _(u"City edge")
        verbose_name_plural = _(u"City edges")

    @property
    def display(self):
        return unicode(self.city)

    @classmethod
    def path_city_edges(self, path):
        return list(set([CityEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=CityEdge.KIND)]))

    @classmethod
    def path_cities(cls, path):
        return [e.city for e in cls.path_city_edges(path)]

    @classmethod
    def topology_city_edges(self, topology):
        s = []
        for p in topology.paths.all():
            s += p.city_edges
        return list(set(s))

    @classmethod
    def topology_cities(cls, topology):
        return [e.city for e in cls.topology_city_edges(topology)]

Path.add_property('city_edges', lambda self: CityEdge.path_city_edges(self))
Path.add_property('cities', lambda self: CityEdge.path_cities(self))
Topology.add_property('city_edges', lambda self: CityEdge.topology_city_edges(self))
Topology.add_property('cities', lambda self: CityEdge.topology_cities(self))


class District(models.Model):
    name = models.CharField(max_length=128, db_column='secteur', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    # Override default manager
    objects = models.GeoManager()

    class Meta:
        db_table = 'couche_secteurs'
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
        db_table = 'secteur'
        verbose_name = _(u"District edge")
        verbose_name_plural = _(u"District edges")

    @property
    def display(self):
        return unicode(self.district)

    @classmethod
    def path_district_edges(self, path):
        return list(set([DistrictEdge.objects.get(pk=t.pk)
                         for t in path.topology_set.existing().filter(
                             kind=DistrictEdge.KIND)]))
    @classmethod
    def path_districts(cls, path):
        return [e.district for e in cls.path_district_edges(path)]

    @classmethod
    def topology_district_edges(self, topology):
        s = []
        for p in topology.paths.all():
            s += p.district_edges
        return list(set(s))

    @classmethod
    def topology_districts(cls, topology):
        return [e.district for e in cls.topology_district_edges(topology)]

Path.add_property('district_edges', lambda self: DistrictEdge.path_district_edges(self))
Path.add_property('districts', lambda self: DistrictEdge.path_districts(self))
Topology.add_property('district_edges', lambda self: DistrictEdge.topology_district_edges(self))
Topology.add_property('districts', lambda self: DistrictEdge.topology_districts(self))
