# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Troncon.classification'
        db.add_column('troncons', 'classification',
                      self.gf('django.db.models.fields.CharField')(default='XX', max_length=2, db_column='type'),
                      keep_default=False)

        # Adding field 'Troncon.district'
        db.add_column('troncons', 'district',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=64, db_column='secteur'),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Troncon.classification'
        db.delete_column('troncons', 'type')

        # Deleting field 'Troncon.district'
        db.delete_column('troncons', 'secteur')


    models = {
        'caminae.evenement': {
            'Meta': {'object_name': 'Evenement', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {}),
            'date_update': ('django.db.models.fields.DateField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.FloatField', [], {'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['caminae.Troncon']", 'through': "orm['caminae.EvenementTroncon']", 'symmetrical': 'False'})
        },
        'caminae.evenementtroncon': {
            'Meta': {'object_name': 'EvenementTroncon', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'evenement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['caminae.Evenement']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'troncon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['caminae.Troncon']"})
        },
        'caminae.troncon': {
            'Meta': {'object_name': 'Troncon', 'db_table': "'troncons'"},
            'classification': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_column': "'type'"}),
            'date_insert': ('django.db.models.fields.DateField', [], {}),
            'date_update': ('django.db.models.fields.DateField', [], {}),
            'district': ('django.db.models.fields.PositiveIntegerField', [], {'db_column': "'secteur'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['caminae']