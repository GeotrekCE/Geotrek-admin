# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlatPage'
        db.create_table('p_t_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert', blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update', blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='public')),
            ('publication_date', self.gf('django.db.models.fields.DateField')(null=True, db_column='date_publication', blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, db_column='titre')),
            ('content', self.gf('django.db.models.fields.TextField')(db_column='contenu', blank=True)),
            ('target', self.gf('django.db.models.fields.CharField')(default='all', max_length=12, db_column='cible')),
        ))
        db.send_create_signal(u'flatpages', ['FlatPage'])

    def backwards(self, orm):
        # Deleting model 'FlatPage'
        db.delete_table('p_t_page')

    models = {
        u'flatpages.flatpage': {
            'Meta': {'object_name': 'FlatPage', 'db_table': "'p_t_page'"},
            'content': ('django.db.models.fields.TextField', [], {'db_column': "'contenu'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'target': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '12', 'db_column': "'cible'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'titre'"})
        }
    }

    complete_apps = ['flatpages']
