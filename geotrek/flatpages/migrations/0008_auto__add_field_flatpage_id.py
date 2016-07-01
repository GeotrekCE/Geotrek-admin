# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field portal on 'FlatPage'
        m2m_table_name = 't_r_page_portal'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flatpage', models.ForeignKey(orm[u'flatpages.flatpage'], null=False)),
            ('targetportal', models.ForeignKey(orm[u'common.targetportal'], null=False))
        ))
        db.create_unique(m2m_table_name, ['flatpage_id', 'targetportal_id'])

    def backwards(self, orm):
        # Removing M2M table for field portal on 'FlatPage'
        db.delete_table('t_r_page_portal')

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
        u'common.targetportal': {
            'Meta': {'ordering': "('name',)", 'object_name': 'TargetPortal', 'db_table': "'o_b_target_portal'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': "'True'", 'max_length': '50'}),
            'website': ('django.db.models.fields.URLField', [], {'unique': "'True'", 'max_length': '256', 'db_column': "'website'"})
        },
        u'flatpages.flatpage': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'FlatPage', 'db_table': "'p_t_page'"},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'contenu'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'db_column': "'url_externe'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'portal': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'flatpages'", 'blank': 'True', 'db_table': "'t_r_page_portal'", 'to': u"orm['common.TargetPortal']"}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'source': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'flatpages'", 'blank': 'True', 'db_table': "'t_r_page_source'", 'to': u"orm['common.RecordSource']"}),
            'target': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '12', 'db_column': "'cible'"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'titre'"})
        }
    }

    complete_apps = ['flatpages']
