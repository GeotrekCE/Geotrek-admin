# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TargetPortal'
        db.create_table('o_b_target_portal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique='True', max_length=50)),
            ('website', self.gf('django.db.models.fields.URLField')(unique='True', max_length=256, db_column='website')),
        ))
        db.send_create_signal(u'common', ['TargetPortal'])


    def backwards(self, orm):
        # Deleting model 'TargetPortal'
        db.delete_table('o_b_target_portal')


    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'cirkwi.cirkwitag': {
            'Meta': {'ordering': "['name']", 'object_name': 'CirkwiTag', 'db_table': "'o_b_cirkwi_tag'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"})
        },
        u'common.filetype': {
            'Meta': {'ordering': "['type']", 'object_name': 'FileType', 'db_table': "'fl_b_fichier'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'common.organism': {
            'Meta': {'ordering': "['organism']", 'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
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
        u'common.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            'cirkwi': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cirkwi.CirkwiTag']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['common']