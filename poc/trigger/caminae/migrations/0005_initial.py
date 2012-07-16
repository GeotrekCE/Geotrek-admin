# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Troncon'
        db.create_table('troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateField')()),
            ('date_update', self.gf('django.db.models.fields.DateField')()),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiLineStringField')(srid=2154)),
            ('classification', self.gf('django.db.models.fields.CharField')(max_length=2, db_column='type')),
            ('district', self.gf('django.db.models.fields.PositiveIntegerField')(db_column='secteur')),
        ))
        db.send_create_signal('caminae', ['Troncon'])

        # Adding model 'Evenement'
        db.create_table('evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateField')()),
            ('date_update', self.gf('django.db.models.fields.DateField')()),
            ('offset', self.gf('django.db.models.fields.FloatField')(db_column='decallage')),
            ('length', self.gf('django.db.models.fields.FloatField')(db_column='longueur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiLineStringField')(srid=2154)),
        ))
        db.send_create_signal('caminae', ['Evenement'])

        # Adding model 'EvenementTroncon'
        db.create_table('evenements_troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('troncon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['caminae.Troncon'])),
            ('evenement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['caminae.Evenement'])),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut')),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin')),
        ))
        db.send_create_signal('caminae', ['EvenementTroncon'])


    def backwards(self, orm):
        # Deleting model 'Troncon'
        db.delete_table('troncons')

        # Deleting model 'Evenement'
        db.delete_table('evenements')

        # Deleting model 'EvenementTroncon'
        db.delete_table('evenements_troncons')


    models = {
        'caminae.evenement': {
            'Meta': {'object_name': 'Evenement', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {}),
            'date_update': ('django.db.models.fields.DateField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'srid': '2154'}),
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
            'geom': ('django.contrib.gis.db.models.fields.MultiLineStringField', [], {'srid': '2154'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['caminae']