# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration
from django.conf import settings
from django.db import connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        """Models were moved from geotrek.land
        """
        if 'l_secteur' in connection.introspection.table_names():
            # Was installed via geotrek.land initial migrations
            # (i.e upgrade to v0.23)
            # See land/migrations/0001_initial.py

            return

        # Adding model 'RestrictedAreaType'
        db.create_table('f_b_zonage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_column='nom')),
        ))
        db.send_create_signal(u'zoning', ['RestrictedAreaType'])

        # Adding model 'RestrictedArea'
        db.create_table('l_zonage_reglementaire', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, db_column='zonage')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=settings.SRID, spatial_index=False)),
            ('area_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zoning.RestrictedAreaType'], db_column='type')),
        ))
        db.send_create_signal(u'zoning', ['RestrictedArea'])

        # Adding model 'RestrictedAreaEdge'
        db.create_table('f_t_zonage', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('restricted_area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zoning.RestrictedArea'], db_column='zone')),
        ))
        db.send_create_signal(u'zoning', ['RestrictedAreaEdge'])

        # Adding model 'City'
        db.create_table('l_commune', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True, db_column='insee')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='commune')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=settings.SRID, spatial_index=False)),
        ))
        db.send_create_signal(u'zoning', ['City'])

        # Adding model 'CityEdge'
        db.create_table('f_t_commune', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zoning.City'], db_column='commune')),
        ))
        db.send_create_signal(u'zoning', ['CityEdge'])

        # Adding model 'District'
        db.create_table('l_secteur', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='secteur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=settings.SRID, spatial_index=False)),
        ))
        db.send_create_signal(u'zoning', ['District'])

        # Adding model 'DistrictEdge'
        db.create_table('f_t_secteur', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['zoning.District'], db_column='secteur')),
        ))
        db.send_create_signal(u'zoning', ['DistrictEdge'])

    def backwards(self, orm):
        """Models were moved from geotrek.land
        """
        # Deleting model 'RestrictedAreaType'
        # db.delete_table('f_b_zonage')

        # Deleting model 'RestrictedArea'
        # db.delete_table('l_zonage_reglementaire')

        # Deleting model 'RestrictedAreaEdge'
        # db.delete_table('f_t_zonage')

        # Deleting model 'City'
        # db.delete_table('l_commune')

        # Deleting model 'CityEdge'
        # db.delete_table('f_t_commune')

        # Deleting model 'District'
        # db.delete_table('l_secteur')

        # Deleting model 'DistrictEdge'
        # db.delete_table('f_t_secteur')

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
        },
        u'zoning.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City', 'db_table': "'l_commune'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True', 'db_column': "'insee'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'commune'"})
        },
        u'zoning.cityedge': {
            'Meta': {'object_name': 'CityEdge', 'db_table': "'f_t_commune'", '_ormbases': [u'core.Topology']},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['zoning.City']", 'db_column': "'commune'"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        u'zoning.district': {
            'Meta': {'ordering': "['name']", 'object_name': 'District', 'db_table': "'l_secteur'"},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'secteur'"})
        },
        u'zoning.districtedge': {
            'Meta': {'object_name': 'DistrictEdge', 'db_table': "'f_t_secteur'", '_ormbases': [u'core.Topology']},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['zoning.District']", 'db_column': "'secteur'"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        u'zoning.restrictedarea': {
            'Meta': {'ordering': "['area_type', 'name']", 'object_name': 'RestrictedArea', 'db_table': "'l_zonage_reglementaire'"},
            'area_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['zoning.RestrictedAreaType']", 'db_column': "'type'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "'zonage'"})
        },
        u'zoning.restrictedareaedge': {
            'Meta': {'object_name': 'RestrictedAreaEdge', 'db_table': "'f_t_zonage'", '_ormbases': [u'core.Topology']},
            'restricted_area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['zoning.RestrictedArea']", 'db_column': "'zone'"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        u'zoning.restrictedareatype': {
            'Meta': {'object_name': 'RestrictedAreaType', 'db_table': "'f_b_zonage'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_column': "'nom'"})
        }
    }

    complete_apps = ['zoning']
