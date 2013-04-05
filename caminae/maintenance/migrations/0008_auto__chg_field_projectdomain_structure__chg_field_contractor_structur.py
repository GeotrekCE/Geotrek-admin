# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'ProjectDomain.structure' to match new field type.
        db.rename_column('m_b_domaine', 'structure_id', 'structure')
        # Changing field 'ProjectDomain.structure'
        db.alter_column('m_b_domaine', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Contractor.structure' to match new field type.
        db.rename_column('m_b_prestataire', 'structure_id', 'structure')
        # Changing field 'Contractor.structure'
        db.alter_column('m_b_prestataire', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Project.structure' to match new field type.
        db.rename_column('m_t_chantier', 'structure_id', 'structure')
        # Changing field 'Project.structure'
        db.alter_column('m_t_chantier', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'InterventionType.structure' to match new field type.
        db.rename_column('m_b_intervention', 'structure_id', 'structure')
        # Changing field 'InterventionType.structure'
        db.alter_column('m_b_intervention', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'InterventionDisorder.structure' to match new field type.
        db.rename_column('m_b_desordre', 'structure_id', 'structure')
        # Changing field 'InterventionDisorder.structure'
        db.alter_column('m_b_desordre', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'InterventionJob.structure' to match new field type.
        db.rename_column('m_b_fonction', 'structure_id', 'structure')
        # Changing field 'InterventionJob.structure'
        db.alter_column('m_b_fonction', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Intervention.structure' to match new field type.
        db.rename_column('m_t_intervention', 'structure_id', 'structure')
        # Changing field 'Intervention.structure'
        db.alter_column('m_t_intervention', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'ProjectType.structure' to match new field type.
        db.rename_column('m_b_chantier', 'structure_id', 'structure')
        # Changing field 'ProjectType.structure'
        db.alter_column('m_b_chantier', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'InterventionStatus.structure' to match new field type.
        db.rename_column('m_b_suivi', 'structure_id', 'structure')
        # Changing field 'InterventionStatus.structure'
        db.alter_column('m_b_suivi', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

    def backwards(self, orm):

        # Renaming column for 'ProjectDomain.structure' to match new field type.
        db.rename_column('m_b_domaine', 'structure', 'structure_id')
        # Changing field 'ProjectDomain.structure'
        db.alter_column('m_b_domaine', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Contractor.structure' to match new field type.
        db.rename_column('m_b_prestataire', 'structure', 'structure_id')
        # Changing field 'Contractor.structure'
        db.alter_column('m_b_prestataire', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Project.structure' to match new field type.
        db.rename_column('m_t_chantier', 'structure', 'structure_id')
        # Changing field 'Project.structure'
        db.alter_column('m_t_chantier', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'InterventionType.structure' to match new field type.
        db.rename_column('m_b_intervention', 'structure', 'structure_id')
        # Changing field 'InterventionType.structure'
        db.alter_column('m_b_intervention', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'InterventionDisorder.structure' to match new field type.
        db.rename_column('m_b_desordre', 'structure', 'structure_id')
        # Changing field 'InterventionDisorder.structure'
        db.alter_column('m_b_desordre', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'InterventionJob.structure' to match new field type.
        db.rename_column('m_b_fonction', 'structure', 'structure_id')
        # Changing field 'InterventionJob.structure'
        db.alter_column('m_b_fonction', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Intervention.structure' to match new field type.
        db.rename_column('m_t_intervention', 'structure', 'structure_id')
        # Changing field 'Intervention.structure'
        db.alter_column('m_t_intervention', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'ProjectType.structure' to match new field type.
        db.rename_column('m_b_chantier', 'structure', 'structure_id')
        # Changing field 'ProjectType.structure'
        db.alter_column('m_b_chantier', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'InterventionStatus.structure' to match new field type.
        db.rename_column('m_b_suivi', 'structure', 'structure_id')
        # Changing field 'InterventionStatus.structure'
        db.alter_column('m_b_suivi', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'common.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"})
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
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
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
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
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
        'maintenance.contractor': {
            'Meta': {'object_name': 'Contractor', 'db_table': "'m_b_prestataire'"},
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'m_r_chantier_financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']"})
        },
        'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'m_t_intervention'"},
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
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'topology': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'to': "orm['core.Topology']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionType']", 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        'maintenance.interventiondisorder': {
            'Meta': {'object_name': 'InterventionDisorder', 'db_table': "'m_b_desordre'"},
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventionjob': {
            'Meta': {'object_name': 'InterventionJob', 'db_table': "'m_b_fonction'"},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'db_column': "'cout_jour'", 'decimal_places': '2', 'max_digits': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventionstatus': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterventionStatus', 'db_table': "'m_b_suivi'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventiontype': {
            'Meta': {'object_name': 'InterventionType', 'db_table': "'m_b_intervention'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
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
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.ProjectType']", 'null': 'True', 'blank': 'True'})
        },
        'maintenance.projectdomain': {
            'Meta': {'object_name': 'ProjectDomain', 'db_table': "'m_b_domaine'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.projecttype': {
            'Meta': {'object_name': 'ProjectType', 'db_table': "'m_b_chantier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['maintenance']