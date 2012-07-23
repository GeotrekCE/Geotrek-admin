# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Trek'
        db.create_table('itineraire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('validated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('length', self.gf('django.db.models.fields.FloatField')()),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description_teaser', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('ambiance', self.gf('django.db.models.fields.TextField')()),
            ('handicapped_infrastructure', self.gf('django.db.models.fields.TextField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('is_park_centered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_transborder', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('advised_parking', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('parking_location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=2154, spatial_index=False)),
            ('public_transport', self.gf('django.db.models.fields.TextField')()),
            ('advice', self.gf('django.db.models.fields.TextField')()),
            ('the_geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
            ('insert_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.Route'])),
            ('difficulty', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.DifficultyLevel'])),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, to=orm['trekking.Destination'])),
        ))
        db.send_create_signal('trekking', ['Trek'])

        # Adding M2M table for field networks on 'Trek'
        db.create_table('itineraire_networks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('treknetwork', models.ForeignKey(orm['trekking.treknetwork'], null=False))
        ))
        db.create_unique('itineraire_networks', ['trek_id', 'treknetwork_id'])

        # Adding M2M table for field usages on 'Trek'
        db.create_table('itineraire_usages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('usage', models.ForeignKey(orm['trekking.usage'], null=False))
        ))
        db.create_unique('itineraire_usages', ['trek_id', 'usage_id'])

        # Adding M2M table for field web_links on 'Trek'
        db.create_table('itineraire_web_links', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm['trekking.trek'], null=False)),
            ('weblink', models.ForeignKey(orm['trekking.weblink'], null=False))
        ))
        db.create_unique('itineraire_web_links', ['trek_id', 'weblink_id'])

        # Adding model 'TrekNetwork'
        db.create_table('reseau', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('trekking', ['TrekNetwork'])

        # Adding model 'Usage'
        db.create_table('usages', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('trekking', ['Usage'])

        # Adding model 'Route'
        db.create_table('parcours', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('trekking', ['Route'])

        # Adding model 'DifficultyLevel'
        db.create_table('classement_difficulte', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('difficulty', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('trekking', ['DifficultyLevel'])

        # Adding model 'Destination'
        db.create_table('destination', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('trekking', ['Destination'])

        # Adding model 'WebLink'
        db.create_table('liens_web', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=128)),
            ('thumbnail', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('trekking', ['WebLink'])


    def backwards(self, orm):
        # Deleting model 'Trek'
        db.delete_table('itineraire')

        # Removing M2M table for field networks on 'Trek'
        db.delete_table('itineraire_networks')

        # Removing M2M table for field usages on 'Trek'
        db.delete_table('itineraire_usages')

        # Removing M2M table for field web_links on 'Trek'
        db.delete_table('itineraire_web_links')

        # Deleting model 'TrekNetwork'
        db.delete_table('reseau')

        # Deleting model 'Usage'
        db.delete_table('usages')

        # Deleting model 'Route'
        db.delete_table('parcours')

        # Deleting model 'DifficultyLevel'
        db.delete_table('classement_difficulte')

        # Deleting model 'Destination'
        db.delete_table('destination')

        # Deleting model 'WebLink'
        db.delete_table('liens_web')


    models = {
        'trekking.destination': {
            'Meta': {'object_name': 'Destination', 'db_table': "'destination'"},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'trekking.difficultylevel': {
            'Meta': {'object_name': 'DifficultyLevel', 'db_table': "'classement_difficulte'"},
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'trekking.route': {
            'Meta': {'object_name': 'Route', 'db_table': "'parcours'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'itineraire'"},
            'advice': ('django.db.models.fields.TextField', [], {}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ambiance': ('django.db.models.fields.TextField', [], {}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_teaser': ('django.db.models.fields.TextField', [], {}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.Destination']"}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.DifficultyLevel']"}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'handicapped_infrastructure': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_transborder': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.TrekNetwork']"}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'public_transport': ('django.db.models.fields.TextField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'to': "orm['trekking.Route']"}),
            'the_geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.Usage']"}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'web_links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'symmetrical': 'False', 'to': "orm['trekking.WebLink']"})
        },
        'trekking.treknetwork': {
            'Meta': {'object_name': 'TrekNetwork', 'db_table': "'reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'trekking.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usages'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'liens_web'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'thumbnail': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['trekking']