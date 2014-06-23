# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ReportStatus'
        db.create_table('f_b_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'feedback', ['ReportStatus'])

        # Adding field 'Report.status'
        db.add_column('f_t_signalement', 'status',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['feedback.ReportStatus'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ReportStatus'
        db.delete_table('f_b_status')

        # Deleting field 'Report.status'
        db.delete_column('f_t_signalement', 'status_id')


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
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'default': 'None', 'srid': '%s' % settings.SRID, 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['feedback.ReportStatus']", 'null': 'True', 'blank': 'True'})
        },
        u'feedback.reportcategory': {
            'Meta': {'object_name': 'ReportCategory', 'db_table': "'f_b_categorie'"},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'feedback.reportstatus': {
            'Meta': {'object_name': 'ReportStatus', 'db_table': "'f_b_status'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['feedback']