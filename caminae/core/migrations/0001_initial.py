# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Path'
        db.create_table('troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
            ('date_insert', self.gf('django.db.models.fields.DateField')()),
            ('date_update', self.gf('django.db.models.fields.DateField')()),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='troncon_valide')),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom')),
            ('length', self.gf('django.db.models.fields.IntegerField')(db_column='longueur')),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_positive')),
            ('descent', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_negative')),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_minimum')),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_maximum')),
        ))
        db.send_create_signal('core', ['Path'])

        # Adding model 'TopologyMixin'
        db.create_table('evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateField')()),
            ('date_update', self.gf('django.db.models.fields.DateField')()),
            ('offset', self.gf('django.db.models.fields.IntegerField')(db_column='decallage')),
            ('length', self.gf('django.db.models.fields.FloatField')(db_column='longueur')),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='supprime')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('core', ['TopologyMixin'])

        # Adding model 'PathAggregation'
        db.create_table('evenements_troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Path'], db_column='troncon')),
            ('topo_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixin'], db_column='evenement')),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut')),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin')),
        ))
        db.send_create_signal('core', ['PathAggregation'])


    def backwards(self, orm):
        # Deleting model 'Path'
        db.delete_table('troncons')

        # Deleting model 'TopologyMixin'
        db.delete_table('evenements')

        # Deleting model 'PathAggregation'
        db.delete_table('evenements_troncons')


    models = {
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'db_column': "'denivelee_positive'"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateField', [], {}),
            'date_update': ('django.db.models.fields.DateField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixin']", 'db_column': "'evenement'"})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {}),
            'date_update': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['core']