# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'ProjectDomain.domain' to match new field type.
        db.rename_column('m_b_domaine', 'domain', 'domaine')
        # Changing field 'ProjectDomain.domain'
        db.alter_column('m_b_domaine', 'domaine', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='domaine'))

        # Renaming column for 'Contractor.contractor' to match new field type.
        db.rename_column('m_b_prestataire', 'contractor', 'prestataire')
        # Changing field 'Contractor.contractor'
        db.alter_column('m_b_prestataire', 'prestataire', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='prestataire'))

        # Renaming column for 'Project.domain' to match new field type.
        db.rename_column('m_t_chantier', 'domain_id', 'domaine')
        # Changing field 'Project.domain'
        db.alter_column('m_t_chantier', 'domaine', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.ProjectDomain'], null=True, db_column='domaine'))

        # Renaming column for 'Project.begin_year' to match new field type.
        db.rename_column('m_t_chantier', 'begin_year', 'annee_debut')
        # Changing field 'Project.begin_year'
        db.alter_column('m_t_chantier', 'annee_debut', self.gf('django.db.models.fields.IntegerField')(db_column='annee_debut'))

        # Renaming column for 'Project.name' to match new field type.
        db.rename_column('m_t_chantier', 'name', 'nom')
        # Changing field 'Project.name'
        db.alter_column('m_t_chantier', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Renaming column for 'Project.project_owner' to match new field type.
        db.rename_column('m_t_chantier', 'project_owner_id', 'maitre_oeuvre')
        # Changing field 'Project.project_owner'
        db.alter_column('m_t_chantier', 'maitre_oeuvre', self.gf('django.db.models.fields.related.ForeignKey')(db_column='maitre_oeuvre', to=orm['common.Organism']))

        # Renaming column for 'Project.constraint' to match new field type.
        db.rename_column('m_t_chantier', 'constraint', 'contraintes')
        # Changing field 'Project.constraint'
        db.alter_column('m_t_chantier', 'contraintes', self.gf('django.db.models.fields.TextField')(db_column='contraintes'))

        # Renaming column for 'Project.end_year' to match new field type.
        db.rename_column('m_t_chantier', 'end_year', 'annee_fin')
        # Changing field 'Project.end_year'
        db.alter_column('m_t_chantier', 'annee_fin', self.gf('django.db.models.fields.IntegerField')(db_column='annee_fin'))

        # Changing field 'Project.date_update'
        db.alter_column('m_t_chantier', 'date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update'))

        # Renaming column for 'Project.comments' to match new field type.
        db.rename_column('m_t_chantier', 'comments', 'commentaires')
        # Changing field 'Project.comments'
        db.alter_column('m_t_chantier', 'commentaires', self.gf('django.db.models.fields.TextField')(db_column='commentaires'))

        # Changing field 'Project.date_insert'
        db.alter_column('m_t_chantier', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert'))

        # Renaming column for 'Project.project_manager' to match new field type.
        db.rename_column('m_t_chantier', 'project_manager_id', 'maitre_ouvrage')
        # Changing field 'Project.project_manager'
        db.alter_column('m_t_chantier', 'maitre_ouvrage', self.gf('django.db.models.fields.related.ForeignKey')(db_column='maitre_ouvrage', to=orm['common.Organism']))

        # Renaming column for 'Project.cost' to match new field type.
        db.rename_column('m_t_chantier', 'cost', 'cout')
        # Changing field 'Project.cost'
        db.alter_column('m_t_chantier', 'cout', self.gf('django.db.models.fields.FloatField')(db_column='cout'))

        # Renaming column for 'Project.type' to match new field type.
        db.rename_column('m_t_chantier', 'type_id', 'type')
        # Changing field 'Project.type'
        db.alter_column('m_t_chantier', 'type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.ProjectType'], null=True, db_column='type'))

        # Changing field 'InterventionType.type'
        db.alter_column('m_b_intervention', 'type', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='type'))

        # Renaming column for 'ManDay.nb_days' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'nb_days', 'nb_jours')
        # Changing field 'ManDay.nb_days'
        db.alter_column('m_r_intervention_fonction', 'nb_jours', self.gf('django.db.models.fields.DecimalField')(db_column='nb_jours', decimal_places=2, max_digits=6))

        # Renaming column for 'ManDay.job' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'job_id', 'fonction')
        # Changing field 'ManDay.job'
        db.alter_column('m_r_intervention_fonction', 'fonction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionJob'], db_column='fonction'))

        # Renaming column for 'ManDay.intervention' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'intervention_id', 'intervention')
        # Changing field 'ManDay.intervention'
        db.alter_column('m_r_intervention_fonction', 'intervention', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Intervention'], db_column='intervention'))

        # Renaming column for 'InterventionDisorder.disorder' to match new field type.
        db.rename_column('m_b_desordre', 'disorder', 'desordre')
        # Changing field 'InterventionDisorder.disorder'
        db.alter_column('m_b_desordre', 'desordre', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='desordre'))

        # Renaming column for 'InterventionJob.job' to match new field type.
        db.rename_column('m_b_fonction', 'job', 'fonction')
        # Changing field 'InterventionJob.job'
        db.alter_column('m_b_fonction', 'fonction', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='fonction'))

        # Renaming column for 'Intervention.slope' to match new field type.
        db.rename_column('m_t_intervention', 'slope', 'pente')
        # Changing field 'Intervention.slope'
        db.alter_column('m_t_intervention', 'pente', self.gf('django.db.models.fields.IntegerField')(db_column='pente'))

        # Changing field 'Intervention.date_update'
        db.alter_column('m_t_intervention', 'date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_column='date_update'))

        # Renaming column for 'Intervention.height' to match new field type.
        db.rename_column('m_t_intervention', 'height', 'hauteur')
        # Changing field 'Intervention.height'
        db.alter_column('m_t_intervention', 'hauteur', self.gf('django.db.models.fields.FloatField')(db_column='hauteur'))

        # Renaming column for 'Intervention.area' to match new field type.
        db.rename_column('m_t_intervention', 'area', 'surface')
        # Changing field 'Intervention.area'
        db.alter_column('m_t_intervention', 'surface', self.gf('django.db.models.fields.IntegerField')(db_column='surface'))

        # Renaming column for 'Intervention.stake' to match new field type.
        db.rename_column('m_t_intervention', 'stake_id', 'enjeu')
        # Changing field 'Intervention.stake'
        db.alter_column('m_t_intervention', 'enjeu', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='enjeu', to=orm['core.Stake']))

        # Renaming column for 'Intervention.comments' to match new field type.
        db.rename_column('m_t_intervention', 'comments', 'commentaire')
        # Changing field 'Intervention.comments'
        db.alter_column('m_t_intervention', 'commentaire', self.gf('django.db.models.fields.TextField')(db_column='commentaire'))

        # Changing field 'Intervention.date_insert'
        db.alter_column('m_t_intervention', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_column='date_insert'))

        # Renaming column for 'Intervention.width' to match new field type.
        db.rename_column('m_t_intervention', 'width', 'largeur')
        # Changing field 'Intervention.width'
        db.alter_column('m_t_intervention', 'largeur', self.gf('django.db.models.fields.FloatField')(db_column='largeur'))

        # Renaming column for 'Intervention.material_cost' to match new field type.
        db.rename_column('m_t_intervention', 'material_cost', 'cout_materiel')
        # Changing field 'Intervention.material_cost'
        db.alter_column('m_t_intervention', 'cout_materiel', self.gf('django.db.models.fields.FloatField')(db_column='cout_materiel'))

        # Renaming column for 'Intervention.status' to match new field type.
        db.rename_column('m_t_intervention', 'status_id', 'status')
        # Changing field 'Intervention.status'
        db.alter_column('m_t_intervention', 'status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionStatus'], db_column='status'))

        # Renaming column for 'Intervention.in_maintenance' to match new field type.
        db.rename_column('m_t_intervention', 'in_maintenance', 'maintenance')
        # Changing field 'Intervention.in_maintenance'
        db.alter_column('m_t_intervention', 'maintenance', self.gf('django.db.models.fields.BooleanField')(db_column='maintenance'))

        # Changing field 'Intervention.date'
        db.alter_column('m_t_intervention', 'date', self.gf('django.db.models.fields.DateField')(db_column='date'))

        # Renaming column for 'Intervention.subcontract_cost' to match new field type.
        db.rename_column('m_t_intervention', 'subcontract_cost', 'cout_soustraitant')
        # Changing field 'Intervention.subcontract_cost'
        db.alter_column('m_t_intervention', 'cout_soustraitant', self.gf('django.db.models.fields.FloatField')(db_column='cout_soustraitant'))

        # Renaming column for 'Intervention.name' to match new field type.
        db.rename_column('m_t_intervention', 'name', 'nom')
        # Changing field 'Intervention.name'
        db.alter_column('m_t_intervention', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Renaming column for 'Intervention.type' to match new field type.
        db.rename_column('m_t_intervention', 'type_id', 'type')
        # Changing field 'Intervention.type'
        db.alter_column('m_t_intervention', 'type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionType'], null=True, db_column='type'))

        # Renaming column for 'Intervention.project' to match new field type.
        db.rename_column('m_t_intervention', 'project_id', 'chantier')
        # Changing field 'Intervention.project'
        db.alter_column('m_t_intervention', 'chantier', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='chantier', to=orm['maintenance.Project']))

        # Renaming column for 'Intervention.length' to match new field type.
        db.rename_column('m_t_intervention', 'length', 'longueur')
        # Changing field 'Intervention.length'
        db.alter_column('m_t_intervention', 'longueur', self.gf('django.db.models.fields.FloatField')(db_column='longueur'))

        # Renaming column for 'Intervention.heliport_cost' to match new field type.
        db.rename_column('m_t_intervention', 'heliport_cost', 'cout_heliport')
        # Changing field 'Intervention.heliport_cost'
        db.alter_column('m_t_intervention', 'cout_heliport', self.gf('django.db.models.fields.FloatField')(db_column='cout_heliport'))

        # Changing field 'ProjectType.type'
        db.alter_column('m_b_chantier', 'type', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='type'))

        # Renaming column for 'Funding.project' to match new field type.
        db.rename_column('m_r_chantier_financement', 'project_id', 'chantier')
        # Changing field 'Funding.project'
        db.alter_column('m_r_chantier_financement', 'chantier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Project'], db_column='chantier'))

        # Renaming column for 'Funding.amount' to match new field type.
        db.rename_column('m_r_chantier_financement', 'amount', 'montant')
        # Changing field 'Funding.amount'
        db.alter_column('m_r_chantier_financement', 'montant', self.gf('django.db.models.fields.FloatField')(db_column='montant'))

        # Renaming column for 'Funding.organism' to match new field type.
        db.rename_column('m_r_chantier_financement', 'organism_id', 'organisme')
        # Changing field 'Funding.organism'
        db.alter_column('m_r_chantier_financement', 'organisme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism'], db_column='organisme'))

        # Changing field 'InterventionStatus.status'
        db.alter_column('m_b_suivi', 'status', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='status'))

    def backwards(self, orm):

        # Renaming column for 'ProjectDomain.domain' to match new field type.
        db.rename_column('m_b_domaine', 'domaine', 'domain')
        # Changing field 'ProjectDomain.domain'
        db.alter_column('m_b_domaine', 'domain', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Contractor.contractor' to match new field type.
        db.rename_column('m_b_prestataire', 'prestataire', 'contractor')
        # Changing field 'Contractor.contractor'
        db.alter_column('m_b_prestataire', 'contractor', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Project.domain' to match new field type.
        db.rename_column('m_t_chantier', 'domaine', 'domain_id')
        # Changing field 'Project.domain'
        db.alter_column('m_t_chantier', 'domain_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.ProjectDomain'], null=True))

        # Renaming column for 'Project.begin_year' to match new field type.
        db.rename_column('m_t_chantier', 'annee_debut', 'begin_year')
        # Changing field 'Project.begin_year'
        db.alter_column('m_t_chantier', 'begin_year', self.gf('django.db.models.fields.IntegerField')())

        # Renaming column for 'Project.name' to match new field type.
        db.rename_column('m_t_chantier', 'nom', 'name')
        # Changing field 'Project.name'
        db.alter_column('m_t_chantier', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Project.project_owner' to match new field type.
        db.rename_column('m_t_chantier', 'maitre_oeuvre', 'project_owner_id')
        # Changing field 'Project.project_owner'
        db.alter_column('m_t_chantier', 'project_owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism']))

        # Renaming column for 'Project.constraint' to match new field type.
        db.rename_column('m_t_chantier', 'contraintes', 'constraint')
        # Changing field 'Project.constraint'
        db.alter_column('m_t_chantier', 'constraint', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Project.end_year' to match new field type.
        db.rename_column('m_t_chantier', 'annee_fin', 'end_year')
        # Changing field 'Project.end_year'
        db.alter_column('m_t_chantier', 'end_year', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Project.date_update'
        db.alter_column('m_t_chantier', 'date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Renaming column for 'Project.comments' to match new field type.
        db.rename_column('m_t_chantier', 'commentaires', 'comments')
        # Changing field 'Project.comments'
        db.alter_column('m_t_chantier', 'comments', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Project.date_insert'
        db.alter_column('m_t_chantier', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Renaming column for 'Project.project_manager' to match new field type.
        db.rename_column('m_t_chantier', 'maitre_ouvrage', 'project_manager_id')
        # Changing field 'Project.project_manager'
        db.alter_column('m_t_chantier', 'project_manager_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism']))

        # Renaming column for 'Project.cost' to match new field type.
        db.rename_column('m_t_chantier', 'cout', 'cost')
        # Changing field 'Project.cost'
        db.alter_column('m_t_chantier', 'cost', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Project.type' to match new field type.
        db.rename_column('m_t_chantier', 'type', 'type_id')
        # Changing field 'Project.type'
        db.alter_column('m_t_chantier', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.ProjectType'], null=True))

        # Changing field 'InterventionType.type'
        db.alter_column('m_b_intervention', 'type', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'ManDay.nb_days' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'nb_jours', 'nb_days')
        # Changing field 'ManDay.nb_days'
        db.alter_column('m_r_intervention_fonction', 'nb_days', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=2))

        # Renaming column for 'ManDay.job' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'fonction', 'job_id')
        # Changing field 'ManDay.job'
        db.alter_column('m_r_intervention_fonction', 'job_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionJob']))

        # Renaming column for 'ManDay.intervention' to match new field type.
        db.rename_column('m_r_intervention_fonction', 'intervention', 'intervention_id')
        # Changing field 'ManDay.intervention'
        db.alter_column('m_r_intervention_fonction', 'intervention_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Intervention']))

        # Renaming column for 'InterventionDisorder.disorder' to match new field type.
        db.rename_column('m_b_desordre', 'desordre', 'disorder')
        # Changing field 'InterventionDisorder.disorder'
        db.alter_column('m_b_desordre', 'disorder', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'InterventionJob.job' to match new field type.
        db.rename_column('m_b_fonction', 'fonction', 'job')
        # Changing field 'InterventionJob.job'
        db.alter_column('m_b_fonction', 'job', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Intervention.slope' to match new field type.
        db.rename_column('m_t_intervention', 'pente', 'slope')
        # Changing field 'Intervention.slope'
        db.alter_column('m_t_intervention', 'slope', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Intervention.date_update'
        db.alter_column('m_t_intervention', 'date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True))

        # Renaming column for 'Intervention.height' to match new field type.
        db.rename_column('m_t_intervention', 'hauteur', 'height')
        # Changing field 'Intervention.height'
        db.alter_column('m_t_intervention', 'height', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Intervention.area' to match new field type.
        db.rename_column('m_t_intervention', 'surface', 'area')
        # Changing field 'Intervention.area'
        db.alter_column('m_t_intervention', 'area', self.gf('django.db.models.fields.IntegerField')())

        # Renaming column for 'Intervention.stake' to match new field type.
        db.rename_column('m_t_intervention', 'enjeu', 'stake_id')
        # Changing field 'Intervention.stake'
        db.alter_column('m_t_intervention', 'stake_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Stake']))

        # Renaming column for 'Intervention.comments' to match new field type.
        db.rename_column('m_t_intervention', 'commentaire', 'comments')
        # Changing field 'Intervention.comments'
        db.alter_column('m_t_intervention', 'comments', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Intervention.date_insert'
        db.alter_column('m_t_intervention', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Renaming column for 'Intervention.width' to match new field type.
        db.rename_column('m_t_intervention', 'largeur', 'width')
        # Changing field 'Intervention.width'
        db.alter_column('m_t_intervention', 'width', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Intervention.material_cost' to match new field type.
        db.rename_column('m_t_intervention', 'cout_materiel', 'material_cost')
        # Changing field 'Intervention.material_cost'
        db.alter_column('m_t_intervention', 'material_cost', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Intervention.status' to match new field type.
        db.rename_column('m_t_intervention', 'status', 'status_id')
        # Changing field 'Intervention.status'
        db.alter_column('m_t_intervention', 'status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionStatus']))

        # Renaming column for 'Intervention.in_maintenance' to match new field type.
        db.rename_column('m_t_intervention', 'maintenance', 'in_maintenance')
        # Changing field 'Intervention.in_maintenance'
        db.alter_column('m_t_intervention', 'in_maintenance', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Intervention.date'
        db.alter_column('m_t_intervention', 'date', self.gf('django.db.models.fields.DateField')())

        # Renaming column for 'Intervention.subcontract_cost' to match new field type.
        db.rename_column('m_t_intervention', 'cout_soustraitant', 'subcontract_cost')
        # Changing field 'Intervention.subcontract_cost'
        db.alter_column('m_t_intervention', 'subcontract_cost', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Intervention.name' to match new field type.
        db.rename_column('m_t_intervention', 'nom', 'name')
        # Changing field 'Intervention.name'
        db.alter_column('m_t_intervention', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Intervention.type' to match new field type.
        db.rename_column('m_t_intervention', 'type', 'type_id')
        # Changing field 'Intervention.type'
        db.alter_column('m_t_intervention', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.InterventionType'], null=True))

        # Renaming column for 'Intervention.project' to match new field type.
        db.rename_column('m_t_intervention', 'chantier', 'project_id')
        # Changing field 'Intervention.project'
        db.alter_column('m_t_intervention', 'project_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['maintenance.Project']))

        # Renaming column for 'Intervention.length' to match new field type.
        db.rename_column('m_t_intervention', 'longueur', 'length')
        # Changing field 'Intervention.length'
        db.alter_column('m_t_intervention', 'length', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Intervention.heliport_cost' to match new field type.
        db.rename_column('m_t_intervention', 'cout_heliport', 'heliport_cost')
        # Changing field 'Intervention.heliport_cost'
        db.alter_column('m_t_intervention', 'heliport_cost', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'ProjectType.type'
        db.alter_column('m_b_chantier', 'type', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Funding.project' to match new field type.
        db.rename_column('m_r_chantier_financement', 'chantier', 'project_id')
        # Changing field 'Funding.project'
        db.alter_column('m_r_chantier_financement', 'project_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maintenance.Project']))

        # Renaming column for 'Funding.amount' to match new field type.
        db.rename_column('m_r_chantier_financement', 'montant', 'amount')
        # Changing field 'Funding.amount'
        db.alter_column('m_r_chantier_financement', 'amount', self.gf('django.db.models.fields.FloatField')())

        # Renaming column for 'Funding.organism' to match new field type.
        db.rename_column('m_r_chantier_financement', 'organisme', 'organism_id')
        # Changing field 'Funding.organism'
        db.alter_column('m_r_chantier_financement', 'organism_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Organism']))

        # Changing field 'InterventionStatus.status'
        db.alter_column('m_b_suivi', 'status', self.gf('django.db.models.fields.CharField')(max_length=128))

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
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'prestataire'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'m_r_chantier_financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'montant'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Organism']", 'db_column': "'organisme'"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']", 'db_column': "'chantier'"})
        },
        'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'m_t_intervention'"},
            'area': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'surface'"}),
            'comments': ('django.db.models.fields.TextField', [], {'db_column': "'commentaire'", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'db_column': "'date'"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'disorders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'interventions'", 'symmetrical': 'False', 'db_table': "'m_r_intervention_desordre'", 'to': "orm['maintenance.InterventionDisorder']"}),
            'height': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'hauteur'"}),
            'heliport_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_heliport'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_maintenance': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'maintenance'"}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.InterventionJob']", 'through': "orm['maintenance.ManDay']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'material_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_materiel'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'interventions'", 'null': 'True', 'db_column': "'chantier'", 'to': "orm['maintenance.Project']"}),
            'slope': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'pente'"}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'db_column': "'enjeu'", 'to': "orm['core.Stake']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionStatus']", 'db_column': "'status'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'cout_soustraitant'"}),
            'topology': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interventions'", 'null': 'True', 'to': "orm['core.Topology']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionType']", 'null': 'True', 'db_column': "'type'", 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'largeur'"})
        },
        'maintenance.interventiondisorder': {
            'Meta': {'object_name': 'InterventionDisorder', 'db_table': "'m_b_desordre'"},
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'desordre'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventionjob': {
            'Meta': {'object_name': 'InterventionJob', 'db_table': "'m_b_fonction'"},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '1.0', 'db_column': "'cout_jour'", 'decimal_places': '2', 'max_digits': '8'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'fonction'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventionstatus': {
            'Meta': {'ordering': "['id']", 'object_name': 'InterventionStatus', 'db_table': "'m_b_suivi'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'status'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.interventiontype': {
            'Meta': {'object_name': 'InterventionType', 'db_table': "'m_b_intervention'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'type'"})
        },
        'maintenance.manday': {
            'Meta': {'object_name': 'ManDay', 'db_table': "'m_r_intervention_fonction'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervention': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Intervention']", 'db_column': "'intervention'"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionJob']", 'db_column': "'fonction'"}),
            'nb_days': ('django.db.models.fields.DecimalField', [], {'db_column': "'nb_jours'", 'decimal_places': '2', 'max_digits': '6'})
        },
        'maintenance.project': {
            'Meta': {'object_name': 'Project', 'db_table': "'m_t_chantier'"},
            'begin_year': ('django.db.models.fields.IntegerField', [], {'db_column': "'annee_debut'"}),
            'comments': ('django.db.models.fields.TextField', [], {'db_column': "'commentaires'", 'blank': 'True'}),
            'constraint': ('django.db.models.fields.TextField', [], {'db_column': "'contraintes'", 'blank': 'True'}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'db_table': "'m_r_chantier_prestataire'", 'to': "orm['maintenance.Contractor']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'cout'"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.ProjectDomain']", 'null': 'True', 'db_column': "'domaine'", 'blank': 'True'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {'db_column': "'annee_fin'"}),
            'founders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['common.Organism']", 'through': "orm['maintenance.Funding']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'project_manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manage'", 'db_column': "'maitre_ouvrage'", 'to': "orm['common.Organism']"}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'own'", 'db_column': "'maitre_oeuvre'", 'to': "orm['common.Organism']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.ProjectType']", 'null': 'True', 'db_column': "'type'", 'blank': 'True'})
        },
        'maintenance.projectdomain': {
            'Meta': {'object_name': 'ProjectDomain', 'db_table': "'m_b_domaine'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'domaine'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'maintenance.projecttype': {
            'Meta': {'object_name': 'ProjectType', 'db_table': "'m_b_chantier'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'type'"})
        }
    }

    complete_apps = ['maintenance']