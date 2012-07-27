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
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
            ('geom_cadastre', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, null=True, spatial_index=False)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True, db_column='troncon_valide')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom_troncon')),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, db_column='remarques')),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0, db_column='longueur')),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_positive')),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_negative')),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_minimum')),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_maximum')),
            ('path_management', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.PathManagement'])),
            ('datasource_management', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.DatasourceManagement'])),
            ('challenge_management', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, to=orm['core.ChallengeManagement'])),
        ))
        db.send_create_signal('core', ['Path'])

        # Adding M2M table for field usages_management on 'Path'
        db.create_table('troncons_usages_management', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('usagemanagement', models.ForeignKey(orm['core.usagemanagement'], null=False))
        ))
        db.create_unique('troncons_usages_management', ['path_id', 'usagemanagement_id'])

        # Adding M2M table for field networks_management on 'Path'
        db.create_table('troncons_networks_management', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm['core.path'], null=False)),
            ('networkmanagement', models.ForeignKey(orm['core.networkmanagement'], null=False))
        ))
        db.create_unique('troncons_networks_management', ['path_id', 'networkmanagement_id'])

        # Adding model 'TopologyMixin'
        db.create_table('evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offset', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='decallage')),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='supprime')),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixinKind'])),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')()),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0, db_column='longueur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
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
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Path'], db_column='troncon')),
            ('topo_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixin'], db_column='evenement')),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut')),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin')),
        ))
        db.send_create_signal('core', ['PathAggregation'])

        # Adding model 'DatasourceManagement'
        db.create_table('gestion_source_donnees', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['DatasourceManagement'])

        # Adding model 'ChallengeManagement'
        db.create_table('gestion_enjeux', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['ChallengeManagement'])

        # Adding model 'UsageManagement'
        db.create_table('gestion_usages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['UsageManagement'])

        # Adding model 'NetworkManagement'
        db.create_table('gestion_reseau', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('core', ['NetworkManagement'])

        # Adding model 'PathManagement'
        db.create_table('gestion_sentier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('comments', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('core', ['PathManagement'])


    def backwards(self, orm):
        # Deleting model 'Path'
        db.delete_table('troncons')

        # Removing M2M table for field usages_management on 'Path'
        db.delete_table('troncons_usages_management')

        # Removing M2M table for field networks_management on 'Path'
        db.delete_table('troncons_networks_management')

        # Deleting model 'TopologyMixin'
        db.delete_table('evenements')

        # Deleting model 'TopologyMixinKind'
        db.delete_table('type_evenements')

        # Deleting model 'PathAggregation'
        db.delete_table('evenements_troncons')

        # Deleting model 'DatasourceManagement'
        db.delete_table('gestion_source_donnees')

        # Deleting model 'ChallengeManagement'
        db.delete_table('gestion_enjeux')

        # Deleting model 'UsageManagement'
        db.delete_table('gestion_usages')

        # Deleting model 'NetworkManagement'
        db.delete_table('gestion_reseau')

        # Deleting model 'PathManagement'
        db.delete_table('gestion_sentier')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.challengemanagement': {
            'Meta': {'object_name': 'ChallengeManagement', 'db_table': "'gestion_enjeux'"},
            'challenge': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.datasourcemanagement': {
            'Meta': {'object_name': 'DatasourceManagement', 'db_table': "'gestion_source_donnees'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.networkmanagement': {
            'Meta': {'object_name': 'NetworkManagement', 'db_table': "'gestion_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'challenge_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.ChallengeManagement']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'datasource_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.DatasourceManagement']"}),
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
            'networks_management': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.NetworkManagement']"}),
            'path_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.PathManagement']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'usages_management': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.UsageManagement']"}),
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
        'core.pathmanagement': {
            'Meta': {'object_name': 'PathManagement', 'db_table': "'gestion_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
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
        'core.usagemanagement': {
            'Meta': {'object_name': 'UsageManagement', 'db_table': "'gestion_usages'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']