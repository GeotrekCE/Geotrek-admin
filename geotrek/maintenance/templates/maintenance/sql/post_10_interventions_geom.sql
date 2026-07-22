-------------------------------------------------------------------------------
-- Keep geometries up-to-date
-------------------------------------------------------------------------------

--
-- Intervention
--

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.update_intervention_geom() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    target_geom geometry;
    target_type_model varchar;
    elevation elevation_infos;
BEGIN
    IF NEW.target_id IS NOT NULL AND NEW.target_type_id IS NOT NULL THEN
        SELECT model FROM django_content_type WHERE id = NEW.target_type_id INTO target_type_model;

        CASE target_type_model
            WHEN 'topology' THEN
                SELECT geom FROM core_topology WHERE id = NEW.target_id INTO target_geom;
            WHEN 'poi' THEN
                SELECT geom FROM core_topology WHERE id = NEW.target_id INTO target_geom;
            WHEN 'infrastructure' THEN
                SELECT geom FROM core_topology WHERE id = NEW.target_id INTO target_geom;
            WHEN 'signage' THEN
                SELECT geom FROM core_topology WHERE id = NEW.target_id INTO target_geom;
            WHEN 'blade' THEN
                SELECT core_topology.geom FROM core_topology 
                JOIN signage_signage ON core_topology.id = signage_signage.topo_object_id
                JOIN signage_blade ON signage_signage.topo_object_id = signage_blade.signage_id
                WHERE signage_blade.id = NEW.target_id INTO target_geom;
            WHEN 'report' THEN
                SELECT geom FROM feedback_report WHERE id = NEW.target_id INTO target_geom;
            WHEN 'site' THEN
                SELECT geom FROM outdoor_site WHERE id = NEW.target_id INTO target_geom;
            WHEN 'course' THEN
                SELECT geom FROM outdoor_course WHERE id = NEW.target_id INTO target_geom;
            ELSE
                target_geom := NULL;
        END CASE;

        NEW.geom := target_geom;
    ELSE
        NEW.geom := NULL;
    END IF;

    IF NEW.geom IS NOT NULL THEN
        SELECT * FROM ft_elevation_infos(NEW.geom, {{ ALTIMETRIC_PROFILE_STEP }}) INTO elevation;

        NEW.geom_3d := elevation.draped;
        NEW.slope := elevation.slope;
        NEW.min_elevation := elevation.min_elevation;
        NEW.max_elevation := elevation.max_elevation;
        NEW.ascent := elevation.positive_gain;
        NEW.descent := elevation.negative_gain;
        IF ST_GeometryType(NEW.geom_3d) <> 'ST_Point' THEN
            NEW.length := ROUND(CAST(ST_LENGTHSPHEROID(ST_TRANSFORM(NEW.geom_3d, 4326), 'SPHEROID["GRS_1980",6378137,298.257222101]') as numeric), 2);
        ELSE
            NEW.length := COALESCE(NEW.length, 0);
        END IF;
    ELSE
        NEW.geom_3d := NULL;
        NEW.length := 0;
        NEW.slope := 0;
        NEW.min_elevation := 0;
        NEW.max_elevation := 0;
        NEW.ascent := 0;
        NEW.descent := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS maintenance_intervention_geom_iu_tgr ON maintenance_intervention;
CREATE TRIGGER maintenance_intervention_geom_iu_tgr
    BEFORE INSERT OR UPDATE OF target_id, target_type_id ON maintenance_intervention
    FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom();


--
-- Trigger on target tables to update intervention geom
--

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.update_intervention_geom_on_target_update() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    _target_type_id integer;
BEGIN
    CASE TG_TABLE_NAME
        WHEN 'core_topology' THEN 
            SELECT id FROM django_content_type WHERE model = 'topology' INTO _target_type_id;
        WHEN 'signage_blade' THEN 
            SELECT id FROM django_content_type WHERE model = 'blade' INTO _target_type_id;
        WHEN 'feedback_report' THEN 
            SELECT id FROM django_content_type WHERE model = 'report' INTO _target_type_id;
        WHEN 'outdoor_site' THEN 
            SELECT id FROM django_content_type WHERE model = 'site' INTO _target_type_id;
        WHEN 'outdoor_course' THEN 
            SELECT id FROM django_content_type WHERE model = 'course' INTO _target_type_id;
        ELSE 
            _target_type_id := NULL;
    END CASE;

    UPDATE maintenance_intervention
    SET geom = CASE 
        WHEN _target_type_id = (SELECT id FROM django_content_type WHERE model = 'blade') THEN
            (SELECT core_topology.geom FROM core_topology 
             JOIN signage_signage ON core_topology.id = signage_signage.topo_object_id
             JOIN signage_blade ON signage_signage.topo_object_id = signage_blade.signage_id
             WHERE signage_blade.id = NEW.id)
        WHEN _target_type_id IN (
            SELECT id FROM django_content_type WHERE model IN ('topology', 'poi', 'infrastructure', 'signage')
        ) THEN
            NEW.geom
        WHEN _target_type_id = (SELECT id FROM django_content_type WHERE model = 'report') THEN
            (SELECT geom FROM feedback_report WHERE id = NEW.id)
        WHEN _target_type_id = (SELECT id FROM django_content_type WHERE model = 'site') THEN
            (SELECT geom FROM outdoor_site WHERE id = NEW.id)
        WHEN _target_type_id = (SELECT id FROM django_content_type WHERE model = 'course') THEN
            (SELECT geom FROM outdoor_course WHERE id = NEW.id)
        ELSE geom 
    END,
    -- Force update of geom_3d and other altimetry fields
    target_id = target_id
    WHERE (target_id = NEW.id AND maintenance_intervention.target_type_id = _target_type_id)
       OR (TG_TABLE_NAME = 'core_topology' AND target_id = NEW.id AND maintenance_intervention.target_type_id IN (
           SELECT id FROM django_content_type WHERE model IN ('topology', 'poi', 'infrastructure', 'signage')
       ));

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS core_topology_intervention_geom_u_tgr ON core_topology;
CREATE TRIGGER core_topology_intervention_geom_u_tgr
AFTER UPDATE OF geom ON core_topology
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

DROP TRIGGER IF EXISTS feedback_report_intervention_geom_u_tgr ON feedback_report;
CREATE TRIGGER feedback_report_intervention_geom_u_tgr
AFTER UPDATE OF geom ON feedback_report
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

DROP TRIGGER IF EXISTS outdoor_site_intervention_geom_u_tgr ON outdoor_site;
CREATE TRIGGER outdoor_site_intervention_geom_u_tgr
AFTER UPDATE OF geom ON outdoor_site
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

DROP TRIGGER IF EXISTS outdoor_course_intervention_geom_u_tgr ON outdoor_course;
CREATE TRIGGER outdoor_course_intervention_geom_u_tgr
AFTER UPDATE OF geom ON outdoor_course
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();


--
-- Project
--

CREATE OR REPLACE FUNCTION {{ schema_geotrek }}.update_project_geom() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    _project_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        _project_id := OLD.project_id;
    ELSE
        _project_id := NEW.project_id;
    END IF;

    IF _project_id IS NOT NULL THEN
        UPDATE maintenance_project SET geom = (
            SELECT ST_ForceCollection(ST_Collect(geom))
            FROM maintenance_intervention 
            WHERE project_id = maintenance_project.id 
              AND deleted = false 
              AND geom IS NOT NULL
        ) WHERE id = _project_id;
    END IF;

    IF TG_OP = 'UPDATE' AND OLD.project_id IS NOT NULL AND OLD.project_id != COALESCE(NEW.project_id, -1) THEN
        UPDATE maintenance_project SET geom = (
            SELECT ST_ForceCollection(ST_Collect(geom))
            FROM maintenance_intervention 
            WHERE project_id = maintenance_project.id 
              AND deleted = false 
              AND geom IS NOT NULL
        ) WHERE id = OLD.project_id;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS maintenance_intervention_project_geom_iu_tgr ON maintenance_intervention;
CREATE TRIGGER maintenance_intervention_project_geom_iu_tgr
AFTER INSERT OR UPDATE OF project_id, geom, deleted ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_project_geom();

DROP TRIGGER IF EXISTS maintenance_intervention_project_geom_d_tgr ON maintenance_intervention;
CREATE TRIGGER maintenance_intervention_project_geom_d_tgr
AFTER DELETE OR UPDATE OF geom ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_project_geom();
