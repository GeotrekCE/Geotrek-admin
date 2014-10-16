# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Organism'
        db.create_table('m_b_organisme', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('organism', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='organisme')),
        ))
        db.send_create_signal(u'common', ['Organism'])

        # Adding model 'FileType'
        db.create_table('fl_b_fichier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
        ))
        db.send_create_signal(u'common', ['FileType'])

    def backwards(self, orm):
        # Deleting model 'Organism'
        db.delete_table('m_b_organisme')

        # Deleting model 'FileType'
        db.delete_table('fl_b_fichier')

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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
        }
    }

    complete_apps = ['common']
