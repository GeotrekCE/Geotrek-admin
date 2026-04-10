-- 10

DROP FUNCTION IF EXISTS delete_related_intervention() CASCADE;
DROP FUNCTION IF EXISTS update_altimetry_evenement_intervention() CASCADE;
DROP FUNCTION IF EXISTS update_altimetry_topology_intervention() CASCADE;
DROP FUNCTION IF EXISTS update_altimetry_intervention() CASCADE;
DROP FUNCTION IF EXISTS update_area_intervention() CASCADE;
DROP FUNCTION IF EXISTS delete_related_intervention_blade() CASCADE;

DROP FUNCTION IF EXISTS update_intervention_geom() CASCADE;
DROP FUNCTION IF EXISTS update_intervention_geom_on_target_update() CASCADE;
DROP FUNCTION IF EXISTS TG_TABLE_NAME_TO_MODEL(table_name varchar) CASCADE;
DROP FUNCTION IF EXISTS update_project_geom() CASCADE;
DROP FUNCTION IF EXISTS delete_related_intervention_report() CASCADE;

-- 20

DROP VIEW IF EXISTS m_v_intervention CASCADE;
DROP VIEW IF EXISTS v_interventions CASCADE;
DROP VIEW IF EXISTS m_v_chantier CASCADE;
DROP VIEW IF EXISTS v_projects CASCADE;
DROP VIEW IF EXISTS v_intervention CASCADE;
DROP VIEW IF EXISTS v_project_qgis CASCADE;