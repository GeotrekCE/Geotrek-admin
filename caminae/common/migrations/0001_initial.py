# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organism'
        db.create_table('liste_de_tous_les_organismes', (
            ('code', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('organism', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('common', ['Organism'])


    def backwards(self, orm):
        # Deleting model 'Organism'
        db.delete_table('liste_de_tous_les_organismes')


    models = {
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['common']