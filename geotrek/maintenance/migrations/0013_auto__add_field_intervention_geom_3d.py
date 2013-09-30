# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Intervention.geom_3d'
        db.add_column('m_t_intervention', 'geom_3d',
                      self.gf('django.contrib.gis.db.models.fields.GeometryField')(default=None, dim=3, spatial_index=False, null=True, srid=settings.SRID),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'Intervention.geom_3d'
        db.delete_column('m_t_intervention', 'geom_3d')


    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'common.organism': {
            'Meta': {'ordering': "['organism']", 'object_name': 'Organism', 'db_table': "'m_b_organisme'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'organisme'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
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
            'geom_3d': ('django.contrib.gis.db.models.fields.LineStringField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
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
            'Meta': {'ordering': "['stake']", 'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
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
            'geom_3d': ('django.contrib.gis.db.models.fields.LineStringField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
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
        u'maintenance.contractor': {
            'Meta': {'ordering': "['contractor']", 'object_name': 'Contractor', 'db_table': "'m_b_prestataire'"},
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'prestataire'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'m_r_chantier_financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'montant'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Organism']", 'db_column': "'organisme'"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.Project']", 'db_column': "'chantier'"})
        },
        u'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'m_t_intervention'"},
            'area': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'surface'"}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'db_column': "'commentaire'", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'db_column': "'date'"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'disorders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'interventions'", 'symmetrical': 'False', 'db_table': "'m_r_intervention_desordre'", 'to': u"orm['maintenance.InterventionDisorder']"}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'hauteur'"}),
            'heliport_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_heliport'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_maintenance': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'maintenance'"}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['maintenance.InterventionJob']", 'through': u"orm['maintenance.ManDay']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'material_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_materiel'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'interventions'", 'null': 'True', 'db_column': "'chantier'", 'to': u"orm['maintenance.Project']"}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'db_column': "'enjeu'", 'to': u"orm['core.Stake']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.InterventionStatus']", 'db_column': "'status'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_soustraitant'"}),
            'topology': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions_set'", 'null': 'True', 'to': u"orm['core.Topology']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.InterventionType']", 'null': 'True', 'db_column': "'type'", 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'largeur'"})
        },
        u'maintenance.interventiondisorder': {
            'Meta': {'ordering': "['disorder']", 'object_name': 'InterventionDisorder', 'db_table': "'m_b_desordre'"},
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'desordre'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'maintenance.interventionjob': {
            'Meta': {'ordering': "['job']", 'object_name': 'InterventionJob', 'db_table': "'m_b_fonction'"},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'db_column': "'cout_jour'", 'decimal_places': '2', 'max_digits': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'fonction'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'maintenance.interventionstatus': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterventionStatus', 'db_table': "'m_b_suivi'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'status'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'maintenance.interventiontype': {
            'Meta': {'ordering': "['type']", 'object_name': 'InterventionType', 'db_table': "'m_b_intervention'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'type'"})
        },
        u'maintenance.manday': {
            'Meta': {'object_name': 'ManDay', 'db_table': "'m_r_intervention_fonction'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervention': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.Intervention']", 'db_column': "'intervention'"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.InterventionJob']", 'db_column': "'fonction'"}),
            'nb_days': ('django.db.models.fields.DecimalField', [], {'db_column': "'nb_jours'", 'decimal_places': '2', 'max_digits': '6'})
        },
        u'maintenance.project': {
            'Meta': {'ordering': "['-begin_year', 'name']", 'object_name': 'Project', 'db_table': "'m_t_chantier'"},
            'begin_year': ('django.db.models.fields.IntegerField', [], {'db_column': "'annee_debut'"}),
            'comments': ('django.db.models.fields.TextField', [], {'db_column': "'commentaires'", 'blank': 'True'}),
            'constraint': ('django.db.models.fields.TextField', [], {'db_column': "'contraintes'", 'blank': 'True'}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'db_table': "'m_r_chantier_prestataire'", 'to': u"orm['maintenance.Contractor']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'cout'"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.ProjectDomain']", 'null': 'True', 'db_column': "'domaine'", 'blank': 'True'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {'db_column': "'annee_fin'"}),
            'founders': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['common.Organism']", 'through': u"orm['maintenance.Funding']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'project_manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manage'", 'db_column': "'maitre_ouvrage'", 'to': u"orm['common.Organism']"}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'own'", 'db_column': "'maitre_oeuvre'", 'to': u"orm['common.Organism']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['maintenance.ProjectType']", 'null': 'True', 'db_column': "'type'", 'blank': 'True'})
        },
        u'maintenance.projectdomain': {
            'Meta': {'ordering': "['domain']", 'object_name': 'ProjectDomain', 'db_table': "'m_b_domaine'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'domaine'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'maintenance.projecttype': {
            'Meta': {'ordering': "['type']", 'object_name': 'ProjectType', 'db_table': "'m_b_chantier'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'type'"})
        }
    }

    complete_apps = ['maintenance']