# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'WorkManagementEdge.organization'
        db.add_column('gestion_travaux', 'organization',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['maintenance.Organism']),
                      keep_default=False)

        # Adding field 'SignageManagementEdge.organization'
        db.add_column('gestion_signaletique', 'organization',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['maintenance.Organism']),
                      keep_default=False)

        # Adding field 'CompetenceEdge.organization'
        db.add_column('competence', 'organization',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['maintenance.Organism']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'WorkManagementEdge.organization'
        db.delete_column('gestion_travaux', 'organization_id')

        # Deleting field 'SignageManagementEdge.organization'
        db.delete_column('gestion_signaletique', 'organization_id')

        # Deleting field 'CompetenceEdge.organization'
        db.delete_column('competence', 'organization_id')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixin']", 'db_column': "'evenement'"})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'land.city': {
            'Meta': {'object_name': 'City', 'db_table': "'couche_communes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True', 'db_column': "'insee'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'commune'"})
        },
        'land.cityedge': {
            'Meta': {'object_name': 'CityEdge', 'db_table': "'commune'", '_ormbases': ['core.TopologyMixin']},
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.competenceedge': {
            'Meta': {'object_name': 'CompetenceEdge', 'db_table': "'competence'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.district': {
            'Meta': {'object_name': 'District', 'db_table': "'couche_secteurs'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_secteur'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'secteur'"})
        },
        'land.districtedge': {
            'Meta': {'object_name': 'DistrictEdge', 'db_table': "'secteur'", '_ormbases': ['core.TopologyMixin']},
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landedge': {
            'Meta': {'object_name': 'LandEdge', 'db_table': "'foncier'", '_ormbases': ['core.TopologyMixin']},
            'land_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.LandType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landtype': {
            'Meta': {'object_name': 'LandType', 'db_table': "'type_foncier'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_foncier'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'foncier'"}),
            'right_of_way': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'droit_de_passage'"})
        },
        'land.physicaledge': {
            'Meta': {'object_name': 'PhysicalEdge', 'db_table': "'nature'", '_ormbases': ['core.TopologyMixin']},
            'physical_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.PhysicalType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.physicaltype': {
            'Meta': {'object_name': 'PhysicalType', 'db_table': "'nature_sentier'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_physique'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'physique'"})
        },
        'land.restrictedarea': {
            'Meta': {'object_name': 'RestrictedArea', 'db_table': "'couche_zonage_reglementaire'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True', 'db_column': "'code_zonage'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'zonage'"}),
            'order': ('django.db.models.fields.IntegerField', [], {'db_column': "'order'"})
        },
        'land.restrictedareaedge': {
            'Meta': {'object_name': 'RestrictedAreaEdge', 'db_table': "'zonage'", '_ormbases': ['core.TopologyMixin']},
            'land_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.RestrictedArea']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.signagemanagementedge': {
            'Meta': {'object_name': 'SignageManagementEdge', 'db_table': "'gestion_signaletique'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.workmanagementedge': {
            'Meta': {'object_name': 'WorkManagementEdge', 'db_table': "'gestion_travaux'", '_ormbases': ['core.TopologyMixin']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.TopologyMixin']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'maintenance.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.TextField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['land']