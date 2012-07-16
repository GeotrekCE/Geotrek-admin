from django.contrib.gis.db import models
from django.conf import settings

# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).

class Path(models.Model):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=False)
    date_insert = models.DateField(editable=False)
    date_update = models.DateField(editable=False)
    valid = models.BooleanField(db_column='troncon_valide')
    code = models.CharField(null=True, max_length=2)
    name = models.CharField(null=True, max_length=128, db_column='nom')
    length = models.IntegerField(editable=False, db_column='longueur')
    ascent = models.IntegerField(
            editable=False, db_column='denivelee_positive')
    descent = models.IntegerField(
            editable=False, db_column='denivelee_negative')
    min_elevation = models.IntegerField(
            editable=False, db_column='altitude_minimum')
    max_elevation = models.IntegerField(
            editable=False, db_column='altitude_maximum')

    objects = models.GeoManager()
    class Meta:
        db_table = 'troncons'

class TopologyMixin(models.Model):
    date_insert = models.DateField(editable=False)
    date_update = models.DateField(editable=False)
    troncons = models.ManyToManyField(Path, through='PathAggregation')
    offset = models.IntegerField(db_column='decallage')
    length = models.FloatField(editable=False, db_column='longueur')
    deleted = models.BooleanField(db_column='supprime')
    geom = models.LineStringField(
            editable=False, srid=settings.SRID, spatial_index=False)
    objects = models.GeoManager()
    class Meta:
        db_table = 'evenements'

class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False, db_column='troncon')
    topo_object = models.ForeignKey(TopologyMixin, null=False, db_column='evenement')
    start_position = models.FloatField(db_column='pk_debut')
    end_position = models.FloatField(db_column='pk_fin')
    class Meta:
        db_table = 'evenements_troncons'
