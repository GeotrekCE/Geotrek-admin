# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        """Fake: filetype is now part of paperclip app"""
        pass

    def backwards(self, orm):
        """Fake: filetype is now part of paperclip app"""
        pass

    models = {
        'common.organism': {
            'Meta': {'ordering': "['organism']", 'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"})
        }
    }

    complete_apps = ['common']