# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataSource'
        db.create_table('t_t_source_donnees', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='titre')),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=400, db_column='url')),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=512, db_column='picto')),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32, db_column='type')),
        ))
        db.send_create_signal(u'tourism', ['DataSource'])

    def backwards(self, orm):
        # Deleting model 'DataSource'
        db.delete_table('t_t_source_donnees')

    models = {
        u'tourism.datasource': {
            'Meta': {'ordering': "['title', 'url']", 'object_name': 'DataSource', 'db_table': "'t_t_source_donnees'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'titre'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_column': "'type'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '400', 'db_column': "'url'"})
        }
    }

    complete_apps = ['tourism']
