# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhysicalType'
        db.create_table('nature_sentier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('land', ['PhysicalType'])

        # Adding model 'PhysicalEdge'
        db.create_table('nature', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('physical_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.PhysicalType'])),
        ))
        db.send_create_signal('land', ['PhysicalEdge'])

        # Adding model 'LandType'
        db.create_table('type_foncier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='foncier')),
            ('right_of_way', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='droit_de_passage')),
        ))
        db.send_create_signal('land', ['LandType'])

        # Adding model 'LandEdge'
        db.create_table('foncier', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('land_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.LandType'])),
        ))
        db.send_create_signal('land', ['LandEdge'])

        # Adding model 'CompetenceEdge'
        db.create_table('competence', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism'])),
        ))
        db.send_create_signal('land', ['CompetenceEdge'])

        # Adding model 'WorkManagementEdge'
        db.create_table('gestion_travaux', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism'])),
        ))
        db.send_create_signal('land', ['WorkManagementEdge'])

        # Adding model 'SignageManagementEdge'
        db.create_table('gestion_signaletique', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism'])),
        ))
        db.send_create_signal('land', ['SignageManagementEdge'])

        # Adding model 'RestrictedArea'
        db.create_table('couche_zonage_reglementaire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='zonage')),
            ('order', self.gf('django.db.models.fields.IntegerField')(db_column='order')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['RestrictedArea'])

        # Adding model 'RestrictedAreaEdge'
        db.create_table('zonage', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('restricted_area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.RestrictedArea'])),
        ))
        db.send_create_signal('land', ['RestrictedAreaEdge'])

        # Adding model 'City'
        db.create_table('couche_communes', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6, primary_key=True, db_column='insee')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='commune')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['City'])

        # Adding model 'CityEdge'
        db.create_table('commune', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.City'])),
        ))
        db.send_create_signal('land', ['CityEdge'])

        # Adding model 'District'
        db.create_table('couche_secteurs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='secteur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=2154, spatial_index=False)),
        ))
        db.send_create_signal('land', ['District'])

        # Adding model 'DistrictEdge'
        db.create_table('secteur', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['land.District'])),
        ))
        db.send_create_signal('land', ['DistrictEdge'])


    def backwards(self, orm):
        # Deleting model 'PhysicalType'
        db.delete_table('nature_sentier')

        # Deleting model 'PhysicalEdge'
        db.delete_table('nature')

        # Deleting model 'LandType'
        db.delete_table('type_foncier')

        # Deleting model 'LandEdge'
        db.delete_table('foncier')

        # Deleting model 'CompetenceEdge'
        db.delete_table('competence')

        # Deleting model 'WorkManagementEdge'
        db.delete_table('gestion_travaux')

        # Deleting model 'SignageManagementEdge'
        db.delete_table('gestion_signaletique')

        # Deleting model 'RestrictedArea'
        db.delete_table('couche_zonage_reglementaire')

        # Deleting model 'RestrictedAreaEdge'
        db.delete_table('zonage')

        # Deleting model 'City'
        db.delete_table('couche_communes')

        # Deleting model 'CityEdge'
        db.delete_table('commune')

        # Deleting model 'District'
        db.delete_table('couche_secteurs')

        # Deleting model 'DistrictEdge'
        db.delete_table('secteur')


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
        'core.challengemanagement': {
            'Meta': {'object_name': 'ChallengeManagement', 'db_table': "'gestion_enjeux'"},
            'challenge': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.datasourcemanagement': {
            'Meta': {'object_name': 'DatasourceManagement', 'db_table': "'gestion_source_donnees'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.networkmanagement': {
            'Meta': {'object_name': 'NetworkManagement', 'db_table': "'gestion_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'challenge_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.ChallengeManagement']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'datasource_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.DatasourceManagement']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'"}),
            'networks_management': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.NetworkManagement']"}),
            'path_management': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.PathManagement']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'usages_management': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['core.UsageManagement']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Topology']", 'db_column': "'evenement'"})
        },
        'core.pathmanagement': {
            'Meta': {'object_name': 'PathManagement', 'db_table': "'gestion_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'comments': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'core.topologykind': {
            'Meta': {'object_name': 'TopologyKind', 'db_table': "'type_evenements'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'core.usagemanagement': {
            'Meta': {'object_name': 'UsageManagement', 'db_table': "'gestion_usages'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'land.city': {
            'Meta': {'object_name': 'City', 'db_table': "'couche_communes'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6', 'primary_key': 'True', 'db_column': "'insee'"}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'commune'"})
        },
        'land.cityedge': {
            'Meta': {'object_name': 'CityEdge', 'db_table': "'commune'", '_ormbases': ['core.Topology']},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.City']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.competenceedge': {
            'Meta': {'object_name': 'CompetenceEdge', 'db_table': "'competence'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.district': {
            'Meta': {'object_name': 'District', 'db_table': "'couche_secteurs'"},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'secteur'"})
        },
        'land.districtedge': {
            'Meta': {'object_name': 'DistrictEdge', 'db_table': "'secteur'", '_ormbases': ['core.Topology']},
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.District']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landedge': {
            'Meta': {'object_name': 'LandEdge', 'db_table': "'foncier'", '_ormbases': ['core.Topology']},
            'land_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.LandType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.landtype': {
            'Meta': {'object_name': 'LandType', 'db_table': "'type_foncier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'foncier'"}),
            'right_of_way': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'droit_de_passage'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'land.physicaledge': {
            'Meta': {'object_name': 'PhysicalEdge', 'db_table': "'nature'", '_ormbases': ['core.Topology']},
            'physical_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.PhysicalType']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.physicaltype': {
            'Meta': {'object_name': 'PhysicalType', 'db_table': "'nature_sentier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'land.restrictedarea': {
            'Meta': {'object_name': 'RestrictedArea', 'db_table': "'couche_zonage_reglementaire'"},
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'zonage'"}),
            'order': ('django.db.models.fields.IntegerField', [], {'db_column': "'order'"})
        },
        'land.restrictedareaedge': {
            'Meta': {'object_name': 'RestrictedAreaEdge', 'db_table': "'zonage'", '_ormbases': ['core.Topology']},
            'restricted_area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['land.RestrictedArea']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.signagemanagementedge': {
            'Meta': {'object_name': 'SignageManagementEdge', 'db_table': "'gestion_signaletique'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        },
        'land.workmanagementedge': {
            'Meta': {'object_name': 'WorkManagementEdge', 'db_table': "'gestion_travaux'", '_ormbases': ['core.Topology']},
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"})
        }
    }

    complete_apps = ['land']