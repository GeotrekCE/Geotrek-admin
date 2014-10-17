# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'DataSource.targets'
        db.alter_column('t_t_source_donnees', 'targets', self.gf('multiselectfield.db.fields.MultiSelectField')(max_length=512, null=True))

    def backwards(self, orm):
        # Changing field 'DataSource.targets'
        db.alter_column('t_t_source_donnees', 'targets', self.gf('multiselectfield.db.fields.MultiSelectField')(max_length=200, null=True))

    models = {
        u'tourism.datasource': {
            'Meta': {'ordering': "['title', 'url']", 'object_name': 'DataSource', 'db_table': "'t_t_source_donnees'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"}),
            'targets': ('multiselectfield.db.fields.MultiSelectField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'titre'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_column': "'type'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '400', 'db_column': "'url'"})
        }
    }

    complete_apps = ['tourism']
