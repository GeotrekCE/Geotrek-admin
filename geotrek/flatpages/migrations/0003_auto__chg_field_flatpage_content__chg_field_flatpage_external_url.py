# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'FlatPage.content'
        db.alter_column('p_t_page', 'contenu', self.gf('django.db.models.fields.TextField')(null=True, db_column='contenu'))

        # Changing field 'FlatPage.external_url'
        db.alter_column('p_t_page', 'url_externe', self.gf('django.db.models.fields.TextField')(null=True, db_column='url_externe'))

    def backwards(self, orm):

        # Changing field 'FlatPage.content'
        db.alter_column('p_t_page', 'contenu', self.gf('django.db.models.fields.TextField')(default='', db_column='contenu'))

        # Changing field 'FlatPage.external_url'
        db.alter_column('p_t_page', 'url_externe', self.gf('django.db.models.fields.TextField')(default='', db_column='url_externe'))

    models = {
        u'flatpages.flatpage': {
            'Meta': {'object_name': 'FlatPage', 'db_table': "'p_t_page'"},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'contenu'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'external_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'url_externe'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'target': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '12', 'db_column': "'cible'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'titre'"})
        }
    }

    complete_apps = ['flatpages']