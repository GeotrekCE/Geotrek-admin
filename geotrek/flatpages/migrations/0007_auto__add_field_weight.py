# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FlatPage.order'
        db.add_column('p_t_page', 'order',
                      self.gf('django.db.models.fields.FloatField')(default=1.0, null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'FlatPage.order'
        db.delete_column('p_t_page', 'order')

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'common.recordsource': {
            'Meta': {'ordering': "['name']", 'object_name': 'RecordSource', 'db_table': "'o_b_source_fiche'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'", 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'flatpages.flatpage': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'FlatPage', 'db_table': "'p_t_page'"},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'contenu'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'db_column': "'url_externe'", 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'source': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'flatpages'", 'to': u"orm['common.RecordSource']", 'db_table': "'t_r_page_source'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '12', 'db_column': "'cible'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'titre'"}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['flatpages']
