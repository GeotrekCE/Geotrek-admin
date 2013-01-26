# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Trek.topology_ptr'
        db.delete_column('o_t_itineraire', 'topology_ptr_id')

        # Adding field 'Trek.topo_object'
        db.add_column('o_t_itineraire', 'topo_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement'),
                      keep_default=False)

        # Deleting field 'POI.topology_ptr'
        db.delete_column('o_t_poi', 'topology_ptr_id')

        # Adding field 'POI.topo_object'
        db.add_column('o_t_poi', 'topo_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement'),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Trek.topology_ptr'
        db.add_column('o_t_itineraire', 'topology_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['core.Topology'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'Trek.topo_object'
        db.delete_column('o_t_itineraire', 'evenement')

        # Adding field 'POI.topology_ptr'
        db.add_column('o_t_poi', 'topology_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=None, to=orm['core.Topology'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'POI.topo_object'
        db.delete_column('o_t_poi', 'evenement')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.comfort': {
            'Meta': {'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'confort'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'reseau'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'confort'", 'to': "orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'source'", 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_insert'"}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_update'"}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'enjeu'", 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'sentier'", 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Usage']", 'db_table': "'l_r_troncon_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'ordering': "['id']", 'object_name': 'PathAggregation', 'db_table': "'e_r_evenement_troncon'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': "orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': "orm['core.Topology']"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'enjeu'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_insert'"}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_update'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'arrivee'"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'db_column': "'commentaire'"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'depart'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'usage'"})
        },
        'trekking.difficultylevel': {
            'Meta': {'object_name': 'DifficultyLevel', 'db_table': "'o_b_difficulte'"},
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'difficulte'"}),
            'difficulty_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'trekking.poi': {
            'Meta': {'object_name': 'POI', 'db_table': "'o_t_poi'", '_ormbases': ['core.Topology']},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'"}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'db_column': "'type'", 'to': "orm['trekking.POIType']"})
        },
        'trekking.poitype': {
            'Meta': {'object_name': 'POIType', 'db_table': "'o_b_poi'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        },
        'trekking.route': {
            'Meta': {'object_name': 'Route', 'db_table': "'o_b_parcours'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parcours'"}),
            'route_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'})
        },
        'trekking.theme': {
            'Meta': {'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        },
        'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'o_t_itineraire'", '_ormbases': ['core.Topology']},
            'access': ('django.db.models.fields.TextField', [], {'db_column': "'acces'", 'blank': 'True'}),
            'access_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'advice': ('django.db.models.fields.TextField', [], {'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parking'", 'blank': 'True'}),
            'ambiance': ('django.db.models.fields.TextField', [], {'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'difficulte'", 'to': "orm['trekking.DifficultyLevel']"}),
            'disabled_infrastructure': ('django.db.models.fields.TextField', [], {'db_column': "'handicap'"}),
            'disabled_infrastructure_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'duree'", 'blank': 'True'}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'coeur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.TrekNetwork']", 'db_table': "'o_r_itineraire_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False', 'db_column': "'geom_parking'", 'blank': 'True'}),
            'public_transport': ('django.db.models.fields.TextField', [], {'db_column': "'transport'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'parcours'", 'to': "orm['trekking.Route']"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.Theme']", 'db_table': "'o_r_itineraire_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.Usage']", 'db_table': "'o_r_itineraire_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'web_links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.WebLink']", 'db_table': "'o_r_itineraire_web'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        'trekking.treknetwork': {
            'Meta': {'object_name': 'TrekNetwork', 'db_table': "'o_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'reseau'"}),
            'network_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'})
        },
        'trekking.trekrelationship': {
            'Meta': {'unique_together': "(('trek_a', 'trek_b'),)", 'object_name': 'TrekRelationship', 'db_table': "'o_r_itineraire_itineraire'"},
            'has_common_departure': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'depart_commun'"}),
            'has_common_edge': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'troncons_communs'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_circuit_step': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'etape_circuit'"}),
            'trek_a': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_a'", 'db_column': "'itineraire_a'", 'to': "orm['trekking.Trek']"}),
            'trek_b': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_b'", 'db_column': "'itineraire_b'", 'to': "orm['trekking.Trek']"})
        },
        'trekking.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'o_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'usage'"}),
            'usage_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'})
        },
        'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'o_t_web'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'db_column': "'categorie'", 'to': "orm['trekking.WebLinkCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128', 'db_column': "'url'"})
        },
        'trekking.weblinkcategory': {
            'Meta': {'object_name': 'WebLinkCategory', 'db_table': "'o_b_web_category'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['trekking']