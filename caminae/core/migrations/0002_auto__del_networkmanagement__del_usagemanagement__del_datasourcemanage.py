# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'NetworkManagement'
        db.delete_table('gestion_reseau')

        # Deleting model 'UsageManagement'
        db.delete_table('gestion_usages')

        # Deleting model 'DatasourceManagement'
        db.delete_table('gestion_source_donnees')

        # Deleting model 'PathManagement'
        db.delete_table('gestion_sentier')

        # Deleting model 'ChallengeManagement'
        db.delete_table('gestion_enjeux')

        # Adding model 'Network'
        db.create_table('reseau', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Network'])

        # Adding model 'Trail'
        db.create_table('sentier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('comments', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['Trail'])

        # Adding model 'Stake'
        db.create_table('enjeu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stake', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Stake'])

        # Adding model 'Usage'
        db.create_table('usage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Usage'])

        # Adding model 'Datasource'
        db.create_table('source_donnees', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['Datasource'])

        # Deleting field 'Path.challenge_management'
        db.delete_column('troncons', 'challenge_management_id')

        # Deleting field 'Path.datasource_management'
        db.delete_column('troncons', 'datasource_management_id')

        # Deleting field 'Path.path_management'
        db.delete_column('troncons', 'path_management_id')

        # Adding field 'Path.trail'
        db.add_column('troncons', 'trail',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Trail']),
                      keep_default=False)

        # Adding field 'Path.datasource'
        db.add_column('troncons', 'datasource',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Datasource']),
                      keep_default=False)

        # Adding field 'Path.stake'
        db.add_column('troncons', 'stake',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.Stake']),
                      keep_default=False)

        # Removing M2M table for field networks_management on 'Path'
        db.delete_table('troncons_networks_management')

        # Removing M2M table for field usages_management on 'Path'
        db.delete_table('troncons_usages_management')

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


    def backwards(self, orm):
        # Adding model 'NetworkManagement'
        db.create_table('gestion_reseau', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['NetworkManagement'])

        # Adding model 'UsageManagement'
        db.create_table('gestion_usages', (
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['UsageManagement'])

        # Adding model 'DatasourceManagement'
        db.create_table('gestion_source_donnees', (
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['DatasourceManagement'])

        # Adding model 'PathManagement'
        db.create_table('gestion_sentier', (
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('comments', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['PathManagement'])

        # Adding model 'ChallengeManagement'
        db.create_table('gestion_enjeux', (
            ('challenge', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('core', ['ChallengeManagement'])

        # Deleting model 'Network'
        db.delete_table('reseau')

        # Deleting model 'Trail'
        db.delete_table('sentier')

        # Deleting model 'Stake'
        db.delete_table('enjeu')

        # Deleting model 'Usage'
        db.delete_table('usage')

        # Deleting model 'Datasource'
        db.delete_table('source_donnees')

        # Adding field 'Path.challenge_management'
        db.add_column('troncons', 'challenge_management',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='paths', null=True, to=orm['core.ChallengeManagement'], blank=True),
                      keep_default=False)

        # Adding field 'Path.datasource_management'
        db.add_column('troncons', 'datasource_management',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='paths', null=True, to=orm['core.DatasourceManagement'], blank=True),
                      keep_default=False)

        # Adding field 'Path.path_management'
        db.add_column('troncons', 'path_management',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='paths', null=True, to=orm['core.PathManagement'], blank=True),
                      keep_default=False)

        # Deleting field 'Path.trail'
        db.delete_column('troncons', 'trail_id')

        # Deleting field 'Path.datasource'
        db.delete_column('troncons', 'datasource_id')

        # Deleting field 'Path.stake'
        db.delete_column('troncons', 'stake_id')

        # Adding M2M table for field networks_management on 'Path'
        db.create_table('troncons_networks_management', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('networkmanagement', models.ForeignKey(orm['core.networkmanagement'], null=False))
        ))
        db.create_unique('troncons_networks_management', ['path_id', 'networkmanagement_id'])

        # Adding M2M table for field usages_management on 'Path'
        db.create_table('troncons_usages_management', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('usagemanagement', models.ForeignKey(orm['core.usagemanagement'], null=False))
        ))
        db.create_unique('troncons_usages_management', ['path_id', 'usagemanagement_id'])

        # Removing M2M table for field usages on 'Path'
        db.delete_table('troncons_usages')

        # Removing M2M table for field networks on 'Path'
        db.delete_table('troncons_networks')


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
            'Meta': {'object_name': 'Network', 'db_table': "'reseau'"},
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
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
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
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixin']", 'db_column': "'evenement'"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixinKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'core.topologymixinkind': {
            'Meta': {'object_name': 'TopologyMixinKind', 'db_table': "'type_evenements'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']