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
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, dim=3, spatial_index=False)),
            ('geom_cadastre', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, dim=3, null=True, spatial_index=False)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True, db_column='troncon_valide')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom_troncon', blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, db_column='remarques', blank=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0, db_column='longueur')),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_positive')),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_negative')),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_minimum')),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_maximum')),
            ('trail', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Trail'])),
            ('datasource', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Datasource'])),
            ('stake', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Stake'])),
        ))
        db.send_create_signal('core', ['Path'])

        # Adding M2M table for field usages on 'Path'
        db.create_table('troncons_usages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('usage', models.ForeignKey(orm['core.usage'], null=False))
        ))
        db.create_unique('troncons_usages', ['path_id', 'usage_id'])

        # Adding M2M table for field networks on 'Path'
        db.create_table('troncons_networks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('network', models.ForeignKey(orm['core.network'], null=False))
        ))
        db.create_unique('troncons_networks', ['path_id', 'network_id'])

        # Adding model 'TopologyMixin'
        db.create_table('evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offset', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='decallage')),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixinKind'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='supprime')),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0, db_column='longueur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.GeometryField')(srid=2154, dim=3, spatial_index=False)),
        ))
        db.send_create_signal('core', ['TopologyMixin'])

        # Adding model 'TopologyMixinKind'
        db.create_table('type_evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('core', ['TopologyMixinKind'])

        # Adding model 'PathAggregation'
        db.create_table('evenements_troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aggregations', db_column='troncon', to=orm['core.Path'])),
            ('topo_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aggregations', db_column='evenement', to=orm['core.TopologyMixin'])),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut')),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin')),
        ))
        db.send_create_signal('core', ['PathAggregation'])

        # Adding model 'Datasource'
        db.create_table('source_donnees', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Datasource'])

        # Adding model 'Stake'
        db.create_table('enjeu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('stake', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Stake'])

        # Adding model 'Usage'
        db.create_table('usage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Usage'])

        # Adding model 'Network'
        db.create_table('reseau_troncon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Network'])

        # Adding model 'Trail'
        db.create_table('sentier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('comments', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('core', ['Trail'])


    def backwards(self, orm):
        # Deleting model 'Path'
        db.delete_table('troncons')

        # Removing M2M table for field usages on 'Path'
        db.delete_table('troncons_usages')

        # Removing M2M table for field networks on 'Path'
        db.delete_table('troncons_networks')

        # Deleting model 'TopologyMixin'
        db.delete_table('evenements')

        # Deleting model 'TopologyMixinKind'
        db.delete_table('type_evenements')

        # Deleting model 'PathAggregation'
        db.delete_table('evenements_troncons')

        # Deleting model 'Datasource'
        db.delete_table('source_donnees')

        # Deleting model 'Stake'
        db.delete_table('enjeu')

        # Deleting model 'Usage'
        db.delete_table('usage')

        # Deleting model 'Network'
        db.delete_table('reseau_troncon')

        # Deleting model 'Trail'
        db.delete_table('sentier')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'source_donnees'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'reseau_troncon'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Network']"}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Usage']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'troncon'", 'to': "orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': "orm['core.TopologyMixin']"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixinKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'})
        },
        'core.topologymixinkind': {
            'Meta': {'object_name': 'TopologyMixinKind', 'db_table': "'type_evenements'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']