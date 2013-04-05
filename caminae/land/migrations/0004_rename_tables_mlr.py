# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('nature_sentier', 'f_b_nature')
        db.rename_table('nature', 'f_t_nature')
        db.rename_table('type_foncier', 'f_b_foncier')
        db.rename_table('foncier', 'f_t_foncier')
        db.rename_table('competence', 'f_t_competence')
        db.rename_table('gestion_travaux', 'f_t_gestion_travaux')
        db.rename_table('gestion_signaletique', 'f_t_gestion_signaletique')
        db.rename_table('bib_typeszones', 'f_b_zonage')
        db.rename_table('couche_zonage_reglementaire', 'l_zonage_reglementaire')
        db.rename_table('zonage', 'f_t_zonage')
        db.rename_table('couche_communes', 'l_commune')
        db.rename_table('commune', 'f_t_commune')
        db.rename_table('couche_secteurs', 'l_secteur')
        db.rename_table('secteur', 'f_t_secteur')

    def backwards(self, orm):
        db.rename_table('f_b_nature', 'nature_sentier')
        db.rename_table('f_t_nature', 'nature')
        db.rename_table('f_b_foncier', 'type_foncier')
        db.rename_table('f_t_foncier', 'foncier')
        db.rename_table('f_t_competence' ,'competence')
        db.rename_table('f_t_gestion_travaux', 'gestion_travaux')
        db.rename_table('f_t_gestion_signaletique', 'gestion_signaletique')
        db.rename_table('f_b_zonage', 'bib_typeszones')
        db.rename_table('l_zonage_reglementaire', 'couche_zonage_reglementaire')
        db.rename_table('f_t_zonage', 'zonage')
        db.rename_table('l_commune', 'couche_communes')
        db.rename_table('f_t_commune', 'commune')
        db.rename_table('l_secteur', 'couche_secteurs')
        db.rename_table('f_t_secteur', 'secteur')

    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.comfort': {
            'Meta': {'object_name': 'Comfort', 'db_table': "'bib_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'source_donnees'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'reseau_troncon'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Network']"}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.Usage']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'ordering': "['id']", 'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': "orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': "orm['core.Topology']"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'land.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City', 'db_table': "'l_communes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True', 'db_column': "'insee'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'commune'"})
        },
        'land.cityedge': {
            'Meta': {'object_name': 'CityEdge', 'db_table': "'f_t_commune'", '_ormbases': ['core.Topology']},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.City']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.competenceedge': {
            'Meta': {'object_name': 'CompetenceEdge', 'db_table': "'f_t_competence'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.district': {
            'Meta': {'ordering': "['name']", 'object_name': 'District', 'db_table': "'l_secteurs'"},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'secteur'"})
        },
        'land.districtedge': {
            'Meta': {'object_name': 'DistrictEdge', 'db_table': "'f_t_secteur'", '_ormbases': ['core.Topology']},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.District']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landedge': {
            'Meta': {'object_name': 'LandEdge', 'db_table': "'f_t_foncier'", '_ormbases': ['core.Topology']},
            'land_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.LandType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landtype': {
            'Meta': {'object_name': 'LandType', 'db_table': "'f_b_foncier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'foncier'"}),
            'right_of_way': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'droit_de_passage'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'land.physicaledge': {
            'Meta': {'object_name': 'PhysicalEdge', 'db_table': "'f_t_nature'", '_ormbases': ['core.Topology']},
            'physical_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.PhysicalType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.physicaltype': {
            'Meta': {'object_name': 'PhysicalType', 'db_table': "'f_b_nature'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'land.restrictedarea': {
            'Meta': {'ordering': "['area_type', 'name']", 'object_name': 'RestrictedArea', 'db_table': "'l_zonage_reglementaire'"},
            'area_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.RestrictedAreaType']"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'db_column': "'zonage'"})
        },
        'land.restrictedareaedge': {
            'Meta': {'object_name': 'RestrictedAreaEdge', 'db_table': "'f_t_zonage'", '_ormbases': ['core.Topology']},
            'restricted_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.RestrictedArea']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.restrictedareatype': {
            'Meta': {'object_name': 'RestrictedAreaType', 'db_table': "'f_b_zonage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'land.signagemanagementedge': {
            'Meta': {'object_name': 'SignageManagementEdge', 'db_table': "'f_t_gestion_signaletique'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.workmanagementedge': {
            'Meta': {'object_name': 'WorkManagementEdge', 'db_table': "'f_t_gestion_travaux'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        }
    }

    complete_apps = ['land']