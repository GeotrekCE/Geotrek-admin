# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from geotrek.authent.models import default_structure


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Organism.structure'
        db.add_column('m_b_organisme', 'structure',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure', default=default_structure().pk),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Organism.structure'
        db.delete_column('m_b_organisme', 'structure')


    models = {
        'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'common.organism': {
            'Meta': {'ordering': "['organism']", 'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        }
    }

    complete_apps = ['common']