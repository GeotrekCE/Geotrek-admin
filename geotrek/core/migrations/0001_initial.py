# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration

from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Path'
        db.create_table('l_t_troncon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert', blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update', blank=True)),
            ('geom_3d', self.gf('django.contrib.gis.db.models.fields.GeometryField')(default=None, dim=3, spatial_index=False, null=True, srid=settings.SRID)),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, db_column='longueur', blank=True)),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='denivelee_positive', blank=True)),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='denivelee_negative', blank=True)),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='altitude_minimum', blank=True)),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='altitude_maximum', blank=True)),
            ('slope', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, db_column='pente', blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=settings.SRID, spatial_index=False)),
            ('geom_cadastre', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=settings.SRID, null=True, spatial_index=False)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True, db_column='valide')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom', blank=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, db_column='remarques', blank=True)),
            ('departure', self.gf('django.db.models.fields.CharField')(default='', max_length=250, null=True, db_column='depart', blank=True)),
            ('arrival', self.gf('django.db.models.fields.CharField')(default='', max_length=250, null=True, db_column='arrivee', blank=True)),
            ('comfort', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, db_column='confort', to=orm['core.Comfort'])),
            ('trail', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, db_column='sentier', to=orm['core.Trail'])),
            ('datasource', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, db_column='source', to=orm['core.Datasource'])),
            ('stake', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='paths', null=True, db_column='enjeu', to=orm['core.Stake'])),
        ))
        db.send_create_signal(u'core', ['Path'])

        # Adding M2M table for field usages on 'Path'
        m2m_table_name = 'l_r_troncon_usage'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm[u'core.path'], null=False)),
            ('usage', models.ForeignKey(orm[u'core.usage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['path_id', 'usage_id'])

        # Adding M2M table for field networks on 'Path'
        m2m_table_name = 'l_r_troncon_reseau'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('path', models.ForeignKey(orm[u'core.path'], null=False)),
            ('network', models.ForeignKey(orm[u'core.network'], null=False))
        ))
        db.create_unique(m2m_table_name, ['path_id', 'network_id'])

        # Adding model 'Topology'
        db.create_table('e_t_evenement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert', blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update', blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='supprime')),
            ('geom_3d', self.gf('django.contrib.gis.db.models.fields.GeometryField')(default=None, dim=3, spatial_index=False, null=True, srid=settings.SRID)),
            ('length', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, db_column='longueur', blank=True)),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='denivelee_positive', blank=True)),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='denivelee_negative', blank=True)),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='altitude_minimum', blank=True)),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='altitude_maximum', blank=True)),
            ('slope', self.gf('django.db.models.fields.FloatField')(default=0.0, null=True, db_column='pente', blank=True)),
            ('offset', self.gf('django.db.models.fields.FloatField')(default=0.0, db_column='decallage')),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.GeometryField')(default=None, srid=settings.SRID, null=True, spatial_index=False)),
        ))
        db.send_create_signal(u'core', ['Topology'])

        # Adding model 'PathAggregation'
        db.create_table('e_r_evenement_troncon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aggregations', on_delete=models.DO_NOTHING, db_column='troncon', to=orm['core.Path'])),
            ('topo_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aggregations', db_column='evenement', to=orm['core.Topology'])),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut', db_index=True)),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin', db_index=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, db_column='ordre', blank=True)),
        ))
        db.send_create_signal(u'core', ['PathAggregation'])

        # Adding model 'Datasource'
        db.create_table('l_b_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'core', ['Datasource'])

        # Adding model 'Stake'
        db.create_table('l_b_enjeu', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('stake', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='enjeu')),
        ))
        db.send_create_signal(u'core', ['Stake'])

        # Adding model 'Comfort'
        db.create_table('l_b_confort', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('comfort', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='confort')),
        ))
        db.send_create_signal(u'core', ['Comfort'])

        # Adding model 'Usage'
        db.create_table('l_b_usage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='usage')),
        ))
        db.send_create_signal(u'core', ['Usage'])

        # Adding model 'Network'
        db.create_table('l_b_reseau', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='reseau')),
        ))
        db.send_create_signal(u'core', ['Network'])

        # Adding model 'Trail'
        db.create_table('l_t_sentier', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure')),
            ('date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert', blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update', blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='nom')),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='depart')),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='arrivee')),
            ('comments', self.gf('django.db.models.fields.TextField')(default='', db_column='commentaire', blank=True)),
        ))
        db.send_create_signal(u'core', ['Trail'])

    def backwards(self, orm):
        # Deleting model 'Path'
        db.delete_table('l_t_troncon')

        # Removing M2M table for field usages on 'Path'
        db.delete_table('l_r_troncon_usage')

        # Removing M2M table for field networks on 'Path'
        db.delete_table('l_r_troncon_reseau')

        # Deleting model 'Topology'
        db.delete_table('e_t_evenement')

        # Deleting model 'PathAggregation'
        db.delete_table('e_r_evenement_troncon')

        # Deleting model 'Datasource'
        db.delete_table('l_b_source')

        # Deleting model 'Stake'
        db.delete_table('l_b_enjeu')

        # Deleting model 'Comfort'
        db.delete_table('l_b_confort')

        # Deleting model 'Usage'
        db.delete_table('l_b_usage')

        # Deleting model 'Network'
        db.delete_table('l_b_reseau')

        # Deleting model 'Trail'
        db.delete_table('l_t_sentier')

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'core.comfort': {
            'Meta': {'ordering': "['comfort']", 'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'confort'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.datasource': {
            'Meta': {'ordering': "['source']", 'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.network': {
            'Meta': {'ordering': "['network']", 'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'reseau'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'confort'", 'to': u"orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'source'", 'to': u"orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': u"orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'enjeu'", 'to': u"orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'sentier'", 'to': u"orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': u"orm['core.Usage']", 'db_table': "'l_r_troncon_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'valide'"})
        },
        u'core.pathaggregation': {
            'Meta': {'ordering': "['id']", 'object_name': 'PathAggregation', 'db_table': "'e_r_evenement_troncon'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'", 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'ordre'", 'blank': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': u"orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'", 'db_index': 'True'}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': u"orm['core.Topology']"})
        },
        u'core.stake': {
            'Meta': {'ordering': "['id']", 'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'enjeu'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Path']", 'through': u"orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'})
        },
        u'core.trail': {
            'Meta': {'ordering': "['name']", 'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'arrivee'"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'db_column': "'commentaire'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'depart'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.usage': {
            'Meta': {'ordering': "['usage']", 'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'usage'"})
        }
    }

    complete_apps = ['core']
