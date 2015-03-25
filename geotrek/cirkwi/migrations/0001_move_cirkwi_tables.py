# -*- coding: utf-8 -*-
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        u'cirkwi.cirkwilocomotion': {
            'Meta': {'ordering': "['name']", 'object_name': 'CirkwiLocomotion', 'db_table': "'o_b_cirkwi_locomotion'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"})
        },
        u'cirkwi.cirkwipoicategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'CirkwiPOICategory', 'db_table': "'o_b_cirkwi_poi_category'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"})
        },
        u'cirkwi.cirkwitag': {
            'Meta': {'ordering': "['name']", 'object_name': 'CirkwiTag', 'db_table': "'o_b_cirkwi_tag'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"})
        }
    }

    complete_apps = ['cirkwi']
