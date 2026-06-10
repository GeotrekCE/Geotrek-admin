-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS maintenance_intervention_date_insert_tgr ON maintenance_intervention;
CREATE TRIGGER maintenance_intervention_date_insert_tgr
    BEFORE INSERT ON maintenance_intervention
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS maintenance_intervention_date_update_tgr ON maintenance_intervention;
CREATE TRIGGER maintenance_intervention_date_update_tgr
    BEFORE INSERT OR UPDATE ON maintenance_intervention
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

DROP TRIGGER IF EXISTS maintenance_project_date_update_tgr ON maintenance_project;
CREATE TRIGGER maintenance_project_date_update_tgr
    BEFORE INSERT OR UPDATE ON maintenance_project
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

-------------------------------------------------------------------------------
-- Delete related interventions when a topology is deleted
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.delete_related_intervention() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    UPDATE maintenance_intervention SET deleted = NEW.deleted WHERE target_id = NEW.id AND target_type_id NOT IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.delete_related_intervention_report() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    UPDATE maintenance_intervention SET deleted = NEW.deleted WHERE target_id = NEW.id AND target_type_id IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'report');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.delete_related_intervention_blade() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    UPDATE maintenance_intervention SET deleted = NEW.deleted WHERE target_id = NEW.id AND target_type_id IN (SELECT id FROM django_content_type  AS ct WHERE ct.model = 'blade');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS maintenance_topology_interventions_d_tgr ON core_topology;
CREATE TRIGGER maintenance_topology_interventions_d_tgr
AFTER UPDATE OF deleted ON core_topology
FOR EACH ROW EXECUTE PROCEDURE delete_related_intervention();

DROP TRIGGER IF EXISTS maintenance_report_interventions_d_tgr ON feedback_report;
CREATE TRIGGER maintenance_report_interventions_d_tgr
AFTER UPDATE OF deleted ON feedback_report
FOR EACH ROW EXECUTE PROCEDURE delete_related_intervention_report();

-------------------------------------------------------------------------------
-- Denormalized altimetry information
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.update_altimetry_topology_intervention() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    UPDATE maintenance_intervention SET
        length = CASE WHEN ST_GeometryType(NEW.geom) <> 'ST_Point' THEN NEW.length ELSE length END,
        slope = NEW.slope,
        min_elevation = NEW.min_elevation, max_elevation = NEW.max_elevation,
        ascent = NEW.ascent, descent = NEW.descent
     WHERE target_id = NEW.id;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS maintenance_topology_interventions_iu_tgr ON core_topology;
CREATE TRIGGER maintenance_topology_interventions_iu_tgr
AFTER UPDATE OF length, slope,
    min_elevation, max_elevation,
    ascent, descent ON core_topology
FOR EACH ROW EXECUTE PROCEDURE update_altimetry_topology_intervention();


CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.update_altimetry_intervention() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    elevation elevation_infos;
BEGIN
    SELECT geom_3d, slope, min_elevation, max_elevation, ascent, descent
    FROM core_topology WHERE id = NEW.target_id INTO elevation;

    IF ST_GeometryType(elevation.draped) <> 'ST_Point' THEN
        NEW.length := ROUND(CAST(ST_LENGTHSPHEROID(ST_TRANSFORM(elevation.draped, 4326), 'SPHEROID["GRS_1980",6378137,298.257222101]') as numeric), 2);
    END IF;
    NEW.geom_3d := elevation.draped;
    NEW.slope := elevation.slope;
    NEW.min_elevation := elevation.min_elevation;
    NEW.max_elevation := elevation.max_elevation;
    NEW.ascent := elevation.positive_gain;
    NEW.descent := elevation.negative_gain;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS m_t_intervention_altimetry_iu_tgr ON maintenance_intervention;
CREATE TRIGGER m_t_intervention_altimetry_iu_tgr
BEFORE INSERT OR UPDATE OF target_id ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_altimetry_intervention();
