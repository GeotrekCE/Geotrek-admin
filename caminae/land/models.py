from django.contrib.gis.db import models
from django.conf import settings
from caminae.core.models import TopologyMixin

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).

# Physcal nature of paths

class PhysicalType(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_physique')
    name = models.CharField(max_length=128, db_column='physique')

    class Meta:
        db_table = 'nature_sentier'

class PhysicalEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')
    physical_type = models.ForeignKey(PhysicalType)

    class Meta:
        db_table = 'nature'

# Type of land under paths

class LandType(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_foncier')
    name = models.CharField(max_length=128, db_column='foncier')
    right_of_way = models.BooleanField(db_column='droit_de_passage')

    class Meta:
        db_table = 'type_foncier'

class LandEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')
    land_type = models.ForeignKey(LandType)

    class Meta:
        db_table = 'foncier'

# Interaction with external structures

class CompetenceEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')

    class Meta:
        db_table = 'competence'

class WorkManagementEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')

    class Meta:
        db_table = 'gestion_travaux'

class SignageManagementEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')

    class Meta:
        db_table = 'gestion_signaletique'

# Zoning

class RestrictedArea(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_zonage')
    name = models.CharField(max_length=128, db_column='zonage')
    order = models.IntegerField(db_column='order')
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    class Meta:
        db_table = 'couche_zonage_reglementaire'

class RestrictedAreaEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')
    land_type = models.ForeignKey(RestrictedArea)

    class Meta:
        db_table = 'zonage'

class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6, db_column='insee')
    name = models.CharField(max_length=128, db_column='commune')
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    class Meta:
        db_table = 'couche_communes'

class CityEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')

    class Meta:
        db_table = 'commune'

class District(models.Model):
    code = models.IntegerField(primary_key=True, db_column='code_secteur')
    name = models.CharField(max_length=128, db_column='secteur')
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)

    class Meta:
        db_table = 'couche_secteurs'

class DistrictEdge(TopologyMixin):
    topo_object = models.OneToOneField(TopologyMixin, parent_link=True, db_column='evenement')

    class Meta:
        db_table = 'secteur'
