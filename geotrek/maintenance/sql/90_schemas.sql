SELECT create_schema_if_not_exist('gestion');

SELECT set_schema('m_v_chantier', 'gestion');
SELECT set_schema('m_v_intervention', 'gestion');

SELECT set_schema_ft('delete_related_intervention()', 'gestion');
SELECT set_schema_ft('update_altimetry_evenement_intervention()', 'gestion');
SELECT set_schema_ft('update_altimetry_intervention()', 'gestion');
SELECT set_schema_ft('update_area_intervention()', 'gestion');
