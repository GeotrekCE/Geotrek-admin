# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'Organism.organism' to match new field type.
        db.rename_column('m_b_organisme', 'organism', 'organisme')
        # Changing field 'Organism.organism'
        db.alter_column('m_b_organisme', 'organisme', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='organisme'))

    def backwards(self, orm):

        # Renaming column for 'Organism.organism' to match new field type.
        db.rename_column('m_b_organisme', 'organisme', 'organism')
        # Changing field 'Organism.organism'
        db.alter_column('m_b_organisme', 'organism', self.gf('django.db.models.fields.CharField')(max_length=128))

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
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"})
        }
    }

    complete_apps = ['common']