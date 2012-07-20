from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from caminae.core.models import TopologyMixin
from caminae.maintenance.models import Organism

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).

# Physcal nature of paths


class PhysicalType(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_physique')
    name = models.CharField(max_length=128, db_column='physique', verbose_name=_(u"Name"))

    class Meta:
        db_table = 'nature_sentier'
        verbose_name = _(u"Physical type")
        verbose_name_plural = _(u"Physical types")

    def __unicode__(self):
        return self.name


class PhysicalEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType, verbose_name=_(u"Physical type"))

    class Meta:
        db_table = 'nature'
        verbose_name = _(u"Physical edge")
        verbose_name_plural = _(u"Physical edges")


# Type of land under paths

class LandType(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_foncier')
    name = models.CharField(max_length=128, db_column='foncier', verbose_name=_(u"Name"))
    right_of_way = models.BooleanField(db_column='droit_de_passage', verbose_name=_(u"Right of way"))

    class Meta:
        db_table = 'type_foncier'
        verbose_name = _(u"Land type")
        verbose_name_plural = _(u"Land types")

    def __unicode__(self):
        return self.name


class LandEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    land_type = models.ForeignKey(LandType, verbose_name=_(u"Land type"))

    class Meta:
        db_table = 'foncier'
        verbose_name = _(u"Land edge")
        verbose_name_plural = _(u"Land edges")


# Interaction with external structures

class CompetenceEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    class Meta:
        db_table = 'competence'
        verbose_name = _(u"Competence edge")
        verbose_name_plural = _(u"Competence edges")


class WorkManagementEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    class Meta:
        db_table = 'gestion_travaux'
        verbose_name = _(u"Work management edge")
        verbose_name_plural = _(u"Work management edges")


class SignageManagementEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True,
                                       db_column='evenement')
    organization = models.ForeignKey(Organism, verbose_name=_(u"Organism"))

    class Meta:
        db_table = 'gestion_signaletique'
        verbose_name = _(u"Signage management edge")
        verbose_name_plural = _(u"Signage management edges")


# Zoning

class RestrictedArea(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_zonage')
    name = models.CharField(max_length=128, db_column='zonage', verbose_name=_(u"Name"))
    order = models.IntegerField(db_column='order', verbose_name=_(u"Order"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

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

    class Meta:
        db_table = 'zonage'
        verbose_name = _(u"Restricted area edge")
        verbose_name_plural = _(u"Restricted area edges")


class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6, db_column='insee')
    name = models.CharField(max_length=128, db_column='commune', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

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

    class Meta:
        db_table = 'commune'
        verbose_name = _(u"City edge")
        verbose_name_plural = _(u"City edges")


class District(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_secteur')
    name = models.CharField(max_length=128, db_column='secteur', verbose_name=_(u"Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

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

    class Meta:
        db_table = 'secteur'
        verbose_name = _(u"District edge")
        verbose_name_plural = _(u"District edges")
