# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Trek.name_en'
        db.add_column('itineraire', 'name_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.name_fr'
        db.add_column('itineraire', 'name_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.name_it'
        db.add_column('itineraire', 'name_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.departure_en'
        db.add_column('itineraire', 'departure_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.departure_fr'
        db.add_column('itineraire', 'departure_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.departure_it'
        db.add_column('itineraire', 'departure_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.arrival_en'
        db.add_column('itineraire', 'arrival_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.arrival_fr'
        db.add_column('itineraire', 'arrival_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.arrival_it'
        db.add_column('itineraire', 'arrival_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_teaser_en'
        db.add_column('itineraire', 'description_teaser_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_teaser_fr'
        db.add_column('itineraire', 'description_teaser_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_teaser_it'
        db.add_column('itineraire', 'description_teaser_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_en'
        db.add_column('itineraire', 'description_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_fr'
        db.add_column('itineraire', 'description_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_it'
        db.add_column('itineraire', 'description_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.ambiance_en'
        db.add_column('itineraire', 'ambiance_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.ambiance_fr'
        db.add_column('itineraire', 'ambiance_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.ambiance_it'
        db.add_column('itineraire', 'ambiance_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.handicapped_infrastructure_en'
        db.add_column('itineraire', 'handicapped_infrastructure_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.handicapped_infrastructure_fr'
        db.add_column('itineraire', 'handicapped_infrastructure_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.handicapped_infrastructure_it'
        db.add_column('itineraire', 'handicapped_infrastructure_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.advice_en'
        db.add_column('itineraire', 'advice_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.advice_fr'
        db.add_column('itineraire', 'advice_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Trek.advice_it'
        db.add_column('itineraire', 'advice_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrekNetwork.network_en'
        db.add_column('reseau', 'network_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrekNetwork.network_fr'
        db.add_column('reseau', 'network_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'TrekNetwork.network_it'
        db.add_column('reseau', 'network_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Usage.usage_en'
        db.add_column('usages', 'usage_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Usage.usage_fr'
        db.add_column('usages', 'usage_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Usage.usage_it'
        db.add_column('usages', 'usage_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'WebLink.name_en'
        db.add_column('liens_web', 'name_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'WebLink.name_fr'
        db.add_column('liens_web', 'name_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'WebLink.name_it'
        db.add_column('liens_web', 'name_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Route.route_en'
        db.add_column('parcours', 'route_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Route.route_fr'
        db.add_column('parcours', 'route_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Route.route_it'
        db.add_column('parcours', 'route_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Destination.destination_en'
        db.add_column('destination', 'destination_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Destination.destination_fr'
        db.add_column('destination', 'destination_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Destination.destination_it'
        db.add_column('destination', 'destination_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DifficultyLevel.difficulty_en'
        db.add_column('classement_difficulte', 'difficulty_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DifficultyLevel.difficulty_fr'
        db.add_column('classement_difficulte', 'difficulty_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DifficultyLevel.difficulty_it'
        db.add_column('classement_difficulte', 'difficulty_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Trek.name_en'
        db.delete_column('itineraire', 'name_en')

        # Deleting field 'Trek.name_fr'
        db.delete_column('itineraire', 'name_fr')

        # Deleting field 'Trek.name_it'
        db.delete_column('itineraire', 'name_it')

        # Deleting field 'Trek.departure_en'
        db.delete_column('itineraire', 'departure_en')

        # Deleting field 'Trek.departure_fr'
        db.delete_column('itineraire', 'departure_fr')

        # Deleting field 'Trek.departure_it'
        db.delete_column('itineraire', 'departure_it')

        # Deleting field 'Trek.arrival_en'
        db.delete_column('itineraire', 'arrival_en')

        # Deleting field 'Trek.arrival_fr'
        db.delete_column('itineraire', 'arrival_fr')

        # Deleting field 'Trek.arrival_it'
        db.delete_column('itineraire', 'arrival_it')

        # Deleting field 'Trek.description_teaser_en'
        db.delete_column('itineraire', 'description_teaser_en')

        # Deleting field 'Trek.description_teaser_fr'
        db.delete_column('itineraire', 'description_teaser_fr')

        # Deleting field 'Trek.description_teaser_it'
        db.delete_column('itineraire', 'description_teaser_it')

        # Deleting field 'Trek.description_en'
        db.delete_column('itineraire', 'description_en')

        # Deleting field 'Trek.description_fr'
        db.delete_column('itineraire', 'description_fr')

        # Deleting field 'Trek.description_it'
        db.delete_column('itineraire', 'description_it')

        # Deleting field 'Trek.ambiance_en'
        db.delete_column('itineraire', 'ambiance_en')

        # Deleting field 'Trek.ambiance_fr'
        db.delete_column('itineraire', 'ambiance_fr')

        # Deleting field 'Trek.ambiance_it'
        db.delete_column('itineraire', 'ambiance_it')

        # Deleting field 'Trek.handicapped_infrastructure_en'
        db.delete_column('itineraire', 'handicapped_infrastructure_en')

        # Deleting field 'Trek.handicapped_infrastructure_fr'
        db.delete_column('itineraire', 'handicapped_infrastructure_fr')

        # Deleting field 'Trek.handicapped_infrastructure_it'
        db.delete_column('itineraire', 'handicapped_infrastructure_it')

        # Deleting field 'Trek.advice_en'
        db.delete_column('itineraire', 'advice_en')

        # Deleting field 'Trek.advice_fr'
        db.delete_column('itineraire', 'advice_fr')

        # Deleting field 'Trek.advice_it'
        db.delete_column('itineraire', 'advice_it')

        # Deleting field 'TrekNetwork.network_en'
        db.delete_column('reseau', 'network_en')

        # Deleting field 'TrekNetwork.network_fr'
        db.delete_column('reseau', 'network_fr')

        # Deleting field 'TrekNetwork.network_it'
        db.delete_column('reseau', 'network_it')

        # Deleting field 'Usage.usage_en'
        db.delete_column('usages', 'usage_en')

        # Deleting field 'Usage.usage_fr'
        db.delete_column('usages', 'usage_fr')

        # Deleting field 'Usage.usage_it'
        db.delete_column('usages', 'usage_it')

        # Deleting field 'WebLink.name_en'
        db.delete_column('liens_web', 'name_en')

        # Deleting field 'WebLink.name_fr'
        db.delete_column('liens_web', 'name_fr')

        # Deleting field 'WebLink.name_it'
        db.delete_column('liens_web', 'name_it')

        # Deleting field 'Route.route_en'
        db.delete_column('parcours', 'route_en')

        # Deleting field 'Route.route_fr'
        db.delete_column('parcours', 'route_fr')

        # Deleting field 'Route.route_it'
        db.delete_column('parcours', 'route_it')

        # Deleting field 'Destination.destination_en'
        db.delete_column('destination', 'destination_en')

        # Deleting field 'Destination.destination_fr'
        db.delete_column('destination', 'destination_fr')

        # Deleting field 'Destination.destination_it'
        db.delete_column('destination', 'destination_it')

        # Deleting field 'DifficultyLevel.difficulty_en'
        db.delete_column('classement_difficulte', 'difficulty_en')

        # Deleting field 'DifficultyLevel.difficulty_fr'
        db.delete_column('classement_difficulte', 'difficulty_fr')

        # Deleting field 'DifficultyLevel.difficulty_it'
        db.delete_column('classement_difficulte', 'difficulty_it')


    models = {
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
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'public_transport': ('django.db.models.fields.TextField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.Route']"}),
            'the_geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
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