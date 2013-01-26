# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_table('interventions_disorders', 'm_r_intervention_desordre')
        db.rename_table('interventions', 'm_t_interventions')
        db.rename_table('bib_de_suivi', 'm_b_suivi')
        db.rename_table('typologie_des_interventions', 'm_b_intervention')
        db.rename_table('desordres', 'm_b_desordre')
        db.rename_table('bib_fonctions', 'm_b_fonction')
        db.rename_table('journeeshomme', 'm_r_intervention_fonction')
        db.rename_table('chantiers_contractors', 'm_r_chantier_prestataire')
        db.rename_table('chantiers', 'm_t_chantier')
        db.rename_table('bib_projet_type', 'm_b_chantier')
        db.rename_table('bib_projet_domaine', 'm_b_domaine')
        db.rename_table('prestataires', 'm_b_prestataire')
        db.rename_table('financement', 'm_r_chantier_financement')

    def backwards(self, orm):
        db.rename_table('m_r_intervention_desordre', 'interventions_disorders')
        db.rename_table('m_t_interventions', 'interventions')
        db.rename_table('m_b_suivi', 'bib_de_suivi')
        db.rename_table('m_b_intervention', 'typologie_des_interventions')
        db.rename_table('m_b_desordre', 'desordres')
        db.rename_table('m_b_fonction', 'bib_fonctions')
        db.rename_table('m_r_intervention_fonction', 'journeeshomme')
        db.rename_table('m_r_chantier_prestataire', 'chantiers_contractors',)
        db.rename_table('m_t_chantier', 'chantiers')
        db.rename_table('m_b_chantier', 'bib_projet_type')
        db.rename_table('m_b_domaine', 'bib_projet_domaine')
        db.rename_table('m_b_prestataire', 'prestataires')
        db.rename_table('m_r_chantier_financement', 'financement')

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
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
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
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
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
        'maintenance.contractor': {
            'Meta': {'object_name': 'Contractor', 'db_table': "'m_b_prestataire'"},
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'m_r_chantier_financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']"})
        },
        'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'m_t_interventions'"},
            'area': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'disorders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'interventions'", 'symmetrical': 'False', 'db_table': "'m_r_intervention_desordre'", 'to': "orm['maintenance.InterventionDisorder']"}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'heliport_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_maintenance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.InterventionJob']", 'through': "orm['maintenance.ManDay']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'material_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'interventions'", 'null': 'True', 'to': "orm['maintenance.Project']"}),
            'slope': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'to': "orm['core.Stake']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionStatus']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'topology': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'to': "orm['core.Topology']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionType']", 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'maintenance.interventiondisorder': {
            'Meta': {'object_name': 'InterventionDisorder', 'db_table': "'m_b_desordre'"},
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionjob': {
            'Meta': {'object_name': 'InterventionJob', 'db_table': "'m_b_fonction'"},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'db_column': "'cout_jour'", 'decimal_places': '2', 'max_digits': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionstatus': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterventionStatus', 'db_table': "'m_b_suivi'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventiontype': {
            'Meta': {'object_name': 'InterventionType', 'db_table': "'m_b_intervention'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'maintenance.manday': {
            'Meta': {'object_name': 'ManDay', 'db_table': "'m_r_intervention_fonction'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervention': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Intervention']"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionJob']"}),
            'nb_days': ('django.db.models.fields.DecimalField', [], {'max_digits': '6', 'decimal_places': '2'})
        },
        'maintenance.project': {
            'Meta': {'object_name': 'Project', 'db_table': "'m_t_chantier'"},
            'begin_year': ('django.db.models.fields.IntegerField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'constraint': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'db_table': "'m_r_chantier_prestataire'", 'to': "orm['maintenance.Contractor']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.ProjectDomain']", 'null': 'True', 'blank': 'True'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {}),
            'founders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.Organism']", 'through': "orm['maintenance.Funding']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project_manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manage'", 'to': "orm['common.Organism']"}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'own'", 'to': "orm['common.Organism']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.ProjectType']", 'null': 'True', 'blank': 'True'})
        },
        'maintenance.projectdomain': {
            'Meta': {'object_name': 'ProjectDomain', 'db_table': "'m_b_domaine'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.projecttype': {
            'Meta': {'object_name': 'ProjectType', 'db_table': "'m_b_chantier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['maintenance']