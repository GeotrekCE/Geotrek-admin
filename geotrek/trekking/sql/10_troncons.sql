SELECT create_schema_if_not_exist('rando');

DROP TRIGGER IF EXISTS l_t_unpublish_trek_d_tgr ON core_path;

CREATE OR REPLACE FUNCTION rando.troncons_unpublish_trek_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    -- Un-published treks because they might be broken
    UPDATE trekking_trek i
        SET public = FALSE
        FROM core_pathaggregation et
        WHERE et.topo_object_id = i.topo_object_id AND et.path_id = OLD.id;


    IF {{PUBLISHED_BY_LANG}} THEN
        UPDATE trekking_trek i
            SET public_{{LANGUAGE_CODE}} = FALSE
            FROM core_pathaggregation et
            WHERE et.topo_object_id = i.topo_object_id AND et.path_id = OLD.id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER l_t_unpublish_trek_d_tgr
BEFORE DELETE ON core_path
FOR EACH ROW EXECUTE PROCEDURE troncons_unpublish_trek_d();
