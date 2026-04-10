-------------------------------------------------------------------------------
-- Keep geometries up-to-date
-------------------------------------------------------------------------------

--
-- Intervention
--

CREATE FUNCTION {{ schema_geotrek }}.update_intervention_geom() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    target_geom geometry;
    target_type_model varchar;
BEGIN
    IF NEW.target_id IS NOT NULL AND NEW.target_type_id IS NOT NULL THEN
        SELECT model FROM django_content_type WHERE id = NEW.target_type_id INTO target_type_model;

        CASE target_type_model
            WHEN 'topology' THEN
                SELECT geom FROM core_topology WHERE id = NEW.target_id INTO target_geom;
            WHEN 'blade' THEN
                SELECT geom FROM core_topology 
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
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintenance_intervention_geom_iu_tgr
BEFORE INSERT OR UPDATE OF target_id, target_type_id ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom();


--
-- Trigger on target tables to update intervention geom
--

CREATE FUNCTION {{ schema_geotrek }}.update_intervention_geom_on_target_update() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    target_type_id integer;
BEGIN
    SELECT id FROM django_content_type WHERE model = TG_TABLE_NAME_TO_MODEL(TG_TABLE_NAME) INTO target_type_id;

    UPDATE maintenance_intervention
    SET geom = CASE 
        WHEN target_type_id = (SELECT id FROM django_content_type WHERE model = 'blade') THEN
            (SELECT core_topology.geom FROM core_topology 
             JOIN signage_signage ON core_topology.id = signage_signage.topo_object_id
             JOIN signage_blade ON signage_signage.id = signage_blade.signage_id
             WHERE signage_blade.id = NEW.id)
        ELSE NEW.geom 
    END
    WHERE target_id = NEW.id AND maintenance_intervention.target_type_id = target_type_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Helper function to map table name to model name
CREATE FUNCTION {{ schema_geotrek }}.TG_TABLE_NAME_TO_MODEL(table_name varchar) RETURNS varchar AS $$
BEGIN
    CASE table_name
        WHEN 'core_topology' THEN RETURN 'topology';
        WHEN 'signage_blade' THEN RETURN 'blade';
        WHEN 'feedback_report' THEN RETURN 'report';
        WHEN 'outdoor_site' THEN RETURN 'site';
        WHEN 'outdoor_course' THEN RETURN 'course';
        ELSE RETURN NULL;
    END CASE;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_topology_intervention_geom_u_tgr
AFTER UPDATE OF geom ON core_topology
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

CREATE TRIGGER feedback_report_intervention_geom_u_tgr
AFTER UPDATE OF geom ON feedback_report
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

CREATE TRIGGER outdoor_site_intervention_geom_u_tgr
AFTER UPDATE OF geom ON outdoor_site
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();

CREATE TRIGGER outdoor_course_intervention_geom_u_tgr
AFTER UPDATE OF geom ON outdoor_course
FOR EACH ROW EXECUTE PROCEDURE update_intervention_geom_on_target_update();


--
-- Project
--

CREATE FUNCTION {{ schema_geotrek }}.update_project_geom() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    project_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        project_id := OLD.project_id;
    ELSE
        project_id := NEW.project_id;
    END IF;

    IF project_id IS NOT NULL THEN
        UPDATE maintenance_project SET geom = (
            SELECT ST_Collect(geom) 
            FROM maintenance_intervention 
            WHERE project_id = maintenance_project.id 
              AND deleted = false 
              AND geom IS NOT NULL
        ) WHERE id = project_id;
    END IF;

    IF TG_OP = 'UPDATE' AND OLD.project_id IS NOT NULL AND OLD.project_id != NEW.project_id THEN
        UPDATE maintenance_project SET geom = (
            SELECT ST_Collect(geom) 
            FROM maintenance_intervention 
            WHERE project_id = maintenance_project.id 
              AND deleted = false 
              AND geom IS NOT NULL
        ) WHERE id = OLD.project_id;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintenance_intervention_project_geom_iu_tgr
AFTER INSERT OR UPDATE OF project_id, geom, deleted ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_project_geom();

CREATE TRIGGER maintenance_intervention_project_geom_d_tgr
AFTER DELETE ON maintenance_intervention
FOR EACH ROW EXECUTE PROCEDURE update_project_geom();
