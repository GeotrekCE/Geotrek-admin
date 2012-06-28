from django.contrib.gis.db import models

class Troncon(models.Model):
    date_insert = models.DateField(editable=False)
    date_update = models.DateField(editable=False)
    valid = models.BooleanField()
    geom = models.MultiLineStringField(srid=2154)
    objects = models.GeoManager()
    classification = models.CharField(null=True, max_length=2, db_column='type')
    district = models.PositiveIntegerField(db_column='secteur')
    class Meta:
        db_table = 'troncons'

class Evenement(models.Model):
    date_insert = models.DateField(editable=False)
    date_update = models.DateField(editable=False)
    troncons = models.ManyToManyField(Troncon, through='EvenementTroncon')
    offset = models.FloatField(db_column='decallage')
    length = models.FloatField(editable=False, db_column='longueur')
    geom = models.MultiLineStringField(editable=False, srid=2154)
    objects = models.GeoManager()
    class Meta:
        db_table = 'evenements'

class EvenementTroncon(models.Model):
    troncon = models.ForeignKey(Troncon, null=False)
    evenement = models.ForeignKey(Evenement, null=False)
    start_position = models.FloatField(db_column='pk_debut')
    end_position = models.FloatField(db_column='pk_fin')
    class Meta:
        db_table = 'evenements_troncons'
