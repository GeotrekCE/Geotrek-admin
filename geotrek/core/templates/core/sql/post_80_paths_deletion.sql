

CREATE FUNCTION {{ schema_geotrek }}.path_deletion() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_count (trigger_id, count_trigger) VALUES("path_deletion", pg_trigger_depth());
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


CREATE FUNCTION {{ schema_geotrek }}.aaaa_log_after_trigger_update() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('AFTER_UPDATE', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER aaaa_log_after_trigger_tgr_update
AFTER UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE aaaa_log_after_trigger_update();

CREATE FUNCTION {{ schema_geotrek }}.aaaa_log_before_trigger_update() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('BEFORE_UPDATE', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER aaaa_log_before_trigger_tgr_update
BEFORE UPDATE OF geom ON core_path
FOR EACH ROW EXECUTE PROCEDURE aaaa_log_before_trigger_update();

CREATE FUNCTION {{ schema_geotrek }}.aaaa_log_after_trigger_insert() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('AFTER_INSERT', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER aaaa_log_after_trigger_tgr_insert
AFTER INSERT ON core_path
FOR EACH ROW EXECUTE PROCEDURE aaaa_log_after_trigger_insert();

CREATE FUNCTION {{ schema_geotrek }}.aaaa_log_before_trigger_insert() RETURNS trigger SECURITY
DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_logs (trigger_type, path_id, created_at, tgr_depth) VALUES('BEFORE_INSERT', NEW.id, clock_timestamp(), pg_trigger_depth());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER aaaa_log_before_trigger_tgr_insert
BEFORE INSERT ON core_path
FOR EACH ROW EXECUTE PROCEDURE aaaa_log_before_trigger_insert();
