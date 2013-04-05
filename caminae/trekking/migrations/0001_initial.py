# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Trek'
        db.create_table('itineraire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('departure_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('departure_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('departure_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('arrival_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('arrival_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('arrival_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('validated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('length', self.gf('django.db.models.fields.FloatField')()),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description_teaser', self.gf('django.db.models.fields.TextField')()),
            ('description_teaser_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_teaser_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_teaser_it', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_it', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ambiance', self.gf('django.db.models.fields.TextField')()),
            ('ambiance_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ambiance_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ambiance_it', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('handicapped_infrastructure', self.gf('django.db.models.fields.TextField')()),
            ('handicapped_infrastructure_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('handicapped_infrastructure_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('handicapped_infrastructure_it', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('is_park_centered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_transborder', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('advised_parking', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('parking_location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=settings.SRID, spatial_index=False)),
            ('public_transport', self.gf('django.db.models.fields.TextField')()),
            ('advice', self.gf('django.db.models.fields.TextField')()),
            ('advice_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('advice_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('advice_it', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=settings.SRID, dim=3, spatial_index=False)),
            ('insert_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.Route'])),
            ('difficulty', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.DifficultyLevel'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.Destination'])),
        ))
        db.send_create_signal('trekking', ['Trek'])

        # Adding M2M table for field networks on 'Trek'
        db.create_table('itineraire_networks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('treknetwork', models.ForeignKey(orm['trekking.treknetwork'], null=False))
        ))
        db.create_unique('itineraire_networks', ['trek_id', 'treknetwork_id'])

        # Adding M2M table for field paths on 'Trek'
        db.create_table('itineraire_paths', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('path', models.ForeignKey(orm['core.path'], null=False))
        ))
        db.create_unique('itineraire_paths', ['trek_id', 'path_id'])

        # Adding M2M table for field usages on 'Trek'
        db.create_table('itineraire_usages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('usage', models.ForeignKey(orm['trekking.usage'], null=False))
        ))
        db.create_unique('itineraire_usages', ['trek_id', 'usage_id'])

        # Adding M2M table for field web_links on 'Trek'
        db.create_table('itineraire_web_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('weblink', models.ForeignKey(orm['trekking.weblink'], null=False))
        ))
        db.create_unique('itineraire_web_links', ['trek_id', 'weblink_id'])

        # Adding model 'TrekNetwork'
        db.create_table('reseau', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('network_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('network_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('network_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('trekking', ['TrekNetwork'])

        # Adding model 'Usage'
        db.create_table('usages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('usage_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('usage_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('usage_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('trekking', ['Usage'])

        # Adding model 'Route'
        db.create_table('parcours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('route_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('route_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('route_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('trekking', ['Route'])

        # Adding model 'DifficultyLevel'
        db.create_table('classement_difficulte', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('difficulty', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('difficulty_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('difficulty_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('difficulty_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('trekking', ['DifficultyLevel'])

        # Adding model 'Destination'
        db.create_table('destination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('destination_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('destination_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('destination_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('trekking', ['Destination'])

        # Adding model 'WebLink'
        db.create_table('liens_web', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=128)),
            ('thumbnail', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('trekking', ['WebLink'])

        # Adding model 'TrekRelationship'
        db.create_table('liens_itineraire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('has_common_departure', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('has_common_edge', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_circuit_step', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('trek_a', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trek_relationship_a', to=orm['trekking.Trek'])),
            ('trek_b', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trek_relationship_b', to=orm['trekking.Trek'])),
        ))
        db.send_create_signal('trekking', ['TrekRelationship'])

        # Adding unique constraint on 'TrekRelationship', fields ['trek_a', 'trek_b']
        db.create_unique('liens_itineraire', ['trek_a_id', 'trek_b_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'TrekRelationship', fields ['trek_a', 'trek_b']
        db.delete_unique('liens_itineraire', ['trek_a_id', 'trek_b_id'])

        # Deleting model 'Trek'
        db.delete_table('itineraire')

        # Removing M2M table for field networks on 'Trek'
        db.delete_table('itineraire_networks')

        # Removing M2M table for field paths on 'Trek'
        db.delete_table('itineraire_paths')

        # Removing M2M table for field usages on 'Trek'
        db.delete_table('itineraire_usages')

        # Removing M2M table for field web_links on 'Trek'
        db.delete_table('itineraire_web_links')

        # Deleting model 'TrekNetwork'
        db.delete_table('reseau')

        # Deleting model 'Usage'
        db.delete_table('usages')

        # Deleting model 'Route'
        db.delete_table('parcours')

        # Deleting model 'DifficultyLevel'
        db.delete_table('classement_difficulte')

        # Deleting model 'Destination'
        db.delete_table('destination')

        # Deleting model 'WebLink'
        db.delete_table('liens_web')

        # Deleting model 'TrekRelationship'
        db.delete_table('liens_itineraire')


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
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
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
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        },
        'trekking.destination': {
            'Meta': {'object_name': 'Destination', 'db_table': "'destination'"},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'destination_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'destination_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'destination_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'trekking.difficultylevel': {
            'Meta': {'object_name': 'DifficultyLevel', 'db_table': "'classement_difficulte'"},
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'difficulty_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'difficulty_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'difficulty_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'trekking.route': {
            'Meta': {'object_name': 'Route', 'db_table': "'parcours'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'route_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'route_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'route_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'itineraire'"},
            'advice': ('django.db.models.fields.TextField', [], {}),
            'advice_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'advice_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'advice_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ambiance': ('django.db.models.fields.TextField', [], {}),
            'ambiance_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ambiance_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ambiance_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'arrival_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'arrival_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'arrival_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'departure_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'departure_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'departure_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {}),
            'description_teaser_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_teaser_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_teaser_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.Destination']"}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.DifficultyLevel']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'handicapped_infrastructure': ('django.db.models.fields.TextField', [], {}),
            'handicapped_infrastructure_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'handicapped_infrastructure_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'handicapped_infrastructure_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_transborder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.TrekNetwork']"}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['core.Path']"}),
            'public_transport': ('django.db.models.fields.TextField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.Route']"}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.Usage']"}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'web_links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.WebLink']"})
        },
        'trekking.treknetwork': {
            'Meta': {'object_name': 'TrekNetwork', 'db_table': "'reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'network_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'network_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'network_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'trekking.trekrelationship': {
            'Meta': {'unique_together': "(('trek_a', 'trek_b'),)", 'object_name': 'TrekRelationship', 'db_table': "'liens_itineraire'"},
            'has_common_departure': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_common_edge': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_circuit_step': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trek_a': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_a'", 'to': "orm['trekking.Trek']"}),
            'trek_b': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_b'", 'to': "orm['trekking.Trek']"})
        },
        'trekking.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usages'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'usage_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'usage_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'usage_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'liens_web'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['trekking']