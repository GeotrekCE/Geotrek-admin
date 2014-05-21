# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Report'
        db.create_table('f_t_signalement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert', blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update', blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('comment', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['feedback.ReportCategory'], null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.PointField')(default=None, srid=settings.SRID, null=True)),
            ('context_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('context_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'feedback', ['Report'])

        # Adding model 'ReportCategory'
        db.create_table('f_b_categorie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'feedback', ['ReportCategory'])


    def backwards(self, orm):
        # Deleting model 'Report'
        db.delete_table('f_t_signalement')

        # Deleting model 'ReportCategory'
        db.delete_table('f_b_categorie')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'feedback.report': {
            'Meta': {'ordering': "['-date_insert']", 'object_name': 'Report', 'db_table': "'f_t_signalement'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['feedback.ReportCategory']", 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'context_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'context_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'default': 'None', 'srid': '%s' % settings.SRID, 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'feedback.reportcategory': {
            'Meta': {'object_name': 'ReportCategory', 'db_table': "'f_b_categorie'"},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['feedback']