# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FileType'
        db.create_table('types_fichiers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('common', ['FileType'])


    def backwards(self, orm):
        # Deleting model 'FileType'
        db.delete_table('types_fichiers')


    models = {
        'common.filetype': {
            'Meta': {'object_name': 'FileType', 'db_table': "'types_fichiers'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['common']