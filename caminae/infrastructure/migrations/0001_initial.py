# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'InfrastructureType'
        db.create_table('classe_amenagement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1, db_column='type')),
        ))
        db.send_create_signal('infrastructure', ['InfrastructureType'])

        # Adding model 'Infrastructure'
        db.create_table('amenagement', (
            ('topology_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['infrastructure.InfrastructureType'])),
        ))
        db.send_create_signal('infrastructure', ['Infrastructure'])


    def backwards(self, orm):
        # Deleting model 'InfrastructureType'
        db.delete_table('classe_amenagement')

        # Deleting model 'Infrastructure'
        db.delete_table('amenagement')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'source_donnees'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'reseau_troncon'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'"}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Network']"}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Usage']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'e_r_evenement_troncon'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Topology']", 'db_column': "'evenement'"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'core.topologykind': {
            'Meta': {'object_name': 'TopologyKind', 'db_table': "'type_evenements'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'infrastructure.infrastructure': {
            'Meta': {'object_name': 'Infrastructure', 'db_table': "'amenagement'", '_ormbases': ['core.Topology']},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'topology_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['infrastructure.InfrastructureType']"})
        },
        'infrastructure.infrastructuretype': {
            'Meta': {'object_name': 'InfrastructureType', 'db_table': "'classe_amenagement'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_column': "'type'"})
        }
    }

    complete_apps = ['infrastructure']