# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CirkwiTag'
        db.create_table('o_b_cirkwi_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eid', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
        ))
        db.send_create_signal(u'common', ['CirkwiTag'])

        # Adding field 'Theme.cirkwi'
        db.add_column('o_b_theme', 'cirkwi',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.CirkwiTag'], null=True, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting model 'CirkwiTag'
        db.delete_table('o_b_cirkwi_tag')

        # Deleting field 'Theme.cirkwi'
        db.delete_column('o_b_theme', 'cirkwi_id')

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'common.cirkwitag': {
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
        u'common.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            'cirkwi': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.CirkwiTag']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['common']
