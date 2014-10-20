SELECT create_schema_if_not_exist('gestion');

SELECT set_schema('m_b_chantier', 'gestion');
SELECT set_schema('m_b_desordre', 'gestion');
SELECT set_schema('m_b_domaine', 'gestion');
SELECT set_schema('m_b_fonction', 'gestion');
SELECT set_schema('m_b_intervention', 'gestion');
SELECT set_schema('m_b_organisme', 'gestion');
SELECT set_schema('m_b_prestataire', 'gestion');
SELECT set_schema('m_b_suivi', 'gestion');
SELECT set_schema('m_r_chantier_financement', 'gestion');
SELECT set_schema('m_r_chantier_prestataire', 'gestion');
SELECT set_schema('m_r_intervention_desordre', 'gestion');
SELECT set_schema('m_r_intervention_fonction', 'gestion');
SELECT set_schema('m_t_chantier', 'gestion');
SELECT set_schema('m_v_chantier', 'gestion');
SELECT set_schema('m_t_intervention', 'gestion');
SELECT set_schema('m_v_intervention', 'gestion');

SELECT set_schema_ft('delete_related_intervention()', 'gestion');
SELECT set_schema_ft('update_altimetry_evenement_intervention()', 'gestion');
SELECT set_schema_ft('update_altimetry_intervention()', 'gestion');
SELECT set_schema_ft('update_area_intervention()', 'gestion');
