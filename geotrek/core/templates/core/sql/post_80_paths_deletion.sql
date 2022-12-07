

CREATE FUNCTION {{ schema_geotrek }}.path_deletion() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    IF {{ ALLOW_PATH_DELETION_TOPOLOGY }} THEN
        RETURN OLD;
    END IF;
    IF EXISTS (SELECT 0 FROM core_pathaggregation et, core_topology e WHERE et.path_id = OLD.id AND et.topo_object_id = e.id)
    THEN
        RAISE WARNING 'You can''.t delete this path, some topologies are linked with this path';
        RETURN NULL;
    ELSE
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER core_path_deletion_topology
BEFORE DELETE ON core_path
FOR EACH ROW EXECUTE PROCEDURE path_deletion();