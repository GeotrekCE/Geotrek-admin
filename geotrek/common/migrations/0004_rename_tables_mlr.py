# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.delete_table('types_fichiers')  # Do not rename, or it will clash with paperclip models
        db.rename_table('liste_de_tous_les_organismes', 'm_b_organisme')

    def backwards(self, orm):
        db.rename_table('m_b_organisme', 'liste_de_tous_les_organismes')

    models = {
        'common.filetype': {
            'Meta': {'object_name': 'FileType', 'db_table': "'fl_b_fichier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'type_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'type_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['common']