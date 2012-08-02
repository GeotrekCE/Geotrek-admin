# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FileType.type_en'
        db.add_column('types_fichiers', 'type_en',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'FileType.type_fr'
        db.add_column('types_fichiers', 'type_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)

        # Adding field 'FileType.type_it'
        db.add_column('types_fichiers', 'type_it',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FileType.type_en'
        db.delete_column('types_fichiers', 'type_en')

        # Deleting field 'FileType.type_fr'
        db.delete_column('types_fichiers', 'type_fr')

        # Deleting field 'FileType.type_it'
        db.delete_column('types_fichiers', 'type_it')


    models = {
        'common.filetype': {
            'Meta': {'object_name': 'FileType', 'db_table': "'types_fichiers'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['common']