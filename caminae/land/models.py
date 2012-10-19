from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from caminae.mapentity.models import MapEntityMixin
from caminae.authent.models import StructureRelated
from caminae.core.models import TopologyMixin, Path
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


class PhysicalEdge(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType, verbose_name=_(u"Physical type"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'nature'
        verbose_name = _(u"Physical edge")
        verbose_name_plural = _(u"Physical edges")

    @property
    def physical_type_display(self):
        return unicode(self.physical_type)


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


class LandEdge(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    land_type = models.ForeignKey(LandType, verbose_name=_(u"Land type"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'foncier'
        verbose_name = _(u"Land edge")
        verbose_name_plural = _(u"Land edges")

    @property
    def land_type_display(self):
        return unicode(self.land_type)

    @classmethod
    def path_lands(self, path):
        return list(set([LandEdge.objects.get(pk=t.pk)
                         for t in path.topologymixin_set.existing().filter(
                             kind=LandEdge.KIND)]))

Path.add_property('lands', lambda self: LandEdge.path_lands(self))




# Interaction with external structures

class CompetenceEdge(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'competence'
        verbose_name = _(u"Competence edge")
        verbose_name_plural = _(u"Competence edges")

    @property
    def organization_display(self):
        return unicode(self.organization)


class WorkManagementEdge(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'gestion_travaux'
        verbose_name = _(u"Work management edge")
        verbose_name_plural = _(u"Work management edges")

    @property
    def organization_display(self):
        return unicode(self.organization)


class SignageManagementEdge(MapEntityMixin, TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'gestion_signaletique'
        verbose_name = _(u"Signage management edge")
        verbose_name_plural = _(u"Signage management edges")

    @property
    def organization_display(self):
        return unicode(self.organization)


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


class RestrictedAreaEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    restricted_area = models.ForeignKey(RestrictedArea, verbose_name=_(u"Restricted area"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'zonage'
        verbose_name = _(u"Restricted area edge")
        verbose_name_plural = _(u"Restricted area edges")


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


class CityEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')

    city = models.ForeignKey(City, verbose_name=_(u"City"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'commune'
        verbose_name = _(u"City edge")
        verbose_name_plural = _(u"City edges")


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


class DistrictEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    district = models.ForeignKey(District, verbose_name=_(u"District"))

    # Override default manager
    objects = TopologyMixin.get_manager_cls(models.GeoManager)()

    class Meta:
        db_table = 'secteur'
        verbose_name = _(u"District edge")
        verbose_name_plural = _(u"District edges")

    @classmethod
    def path_districts(self, path):
        return list(set([DistrictEdge.objects.get(pk=t.pk).district
                         for t in path.topologymixin_set.existing().filter(
                             kind=DistrictEdge.KIND)]))

    @classmethod
    def topology_districts(self, topology):
        s = []
        for p in topology.paths.all():
            s += p.districts
        return list(set(s))

Path.add_property('districts', lambda self: DistrictEdge.path_districts(self))
TopologyMixin.add_property('districts', lambda self: DistrictEdge.topology_districts(self))
