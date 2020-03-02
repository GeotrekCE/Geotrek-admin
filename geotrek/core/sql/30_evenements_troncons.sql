-------------------------------------------------------------------------------
-- Alter FK to troncon in order to add CASCADE behavior at DB-level
-------------------------------------------------------------------------------

DO LANGUAGE plpgsql $$
DECLARE
    fk_name varchar;
BEGIN
    -- Obtain FK name (which is dynamically generated when table is created)
    SELECT c.conname INTO fk_name
        FROM pg_class t1, pg_class t2, pg_constraint c
        WHERE t1.relname = 'core_pathaggregation' AND c.conrelid = t1.oid
          AND t2.relname = 'core_path' AND c.confrelid = t2.oid
          AND c.contype = 'f';
    -- Use a dynamic SQL statement with the name found
    IF fk_name IS NOT NULL THEN
        EXECUTE 'ALTER TABLE core_pathaggregation DROP CONSTRAINT ' || quote_ident(fk_name);
    END IF;
END;
$$;

-- Now re-create the FK with cascade option
ALTER TABLE core_pathaggregation ADD FOREIGN KEY (path_id) REFERENCES core_path(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


-------------------------------------------------------------------------------
-- Evenements utilities
-------------------------------------------------------------------------------

DROP FUNCTION IF EXISTS geotrek.ft_troncon_interpolate(integer, geometry);

CREATE OR REPLACE FUNCTION geotrek.ft_troncon_interpolate(path integer, point geometry) RETURNS RECORD AS $$
DECLARE 
  line GEOMETRY;
  result RECORD;
BEGIN
    SELECT geom FROM core_path WHERE id=path INTO line;
    SELECT * FROM ST_InterpolateAlong(line, point) AS (position FLOAT, distance FLOAT) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Compute geometry of Evenements
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_r_evenement_troncon_geometry_tgr ON core_pathaggregation;

CREATE OR REPLACE FUNCTION geotrek.ft_evenements_troncons_geometry() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    eid integer;
    eids integer[];
BEGIN
    IF TG_OP = 'INSERT' THEN
        eids := array_append(eids, NEW.topo_object_id);
    ELSE
        eids := array_append(eids, OLD.topo_object_id);
        IF TG_OP = 'UPDATE' THEN -- /!\ Logical ops are commutative in SQL
            IF NEW.topo_object_id != OLD.topo_object_id THEN
                eids := array_append(eids, NEW.topo_object_id);
            END IF;
        END IF;
    END IF;

    FOREACH eid IN ARRAY eids LOOP
        PERFORM update_geometry_of_evenement(eid);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER e_r_evenement_troncon_geometry_tgr
AFTER INSERT OR UPDATE OR DELETE ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_geometry();


-------------------------------------------------------------------------------
-- Emulate junction points
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_r_evenement_troncon_junction_point_iu_tgr ON core_pathaggregation;

CREATE OR REPLACE FUNCTION geotrek.ft_evenements_troncons_junction_point_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    junction geometry;
    t_count integer;
BEGIN
    -- Deal with previously connected paths in the case of an UDPATE action
    IF TG_OP = 'UPDATE' THEN
        -- There were connected paths only if it was a junction point
        IF OLD.start_position = OLD.end_position AND OLD.start_position IN (0.0, 1.0) THEN
            DELETE FROM core_pathaggregation
            WHERE id != OLD.id AND topo_object_id = OLD.topo_object_id;
        END IF;
    END IF;

    -- Don't proceed for non-junction points
    IF NEW.start_position != NEW.end_position OR NEW.start_position NOT IN (0.0, 1.0) THEN
        RETURN NULL;
    END IF;

    -- Don't proceed for intermediate markers (forced passage) : if this 
    -- is not the only evenement_troncon, then it's an intermediate marker.
    SELECT count(*)
        INTO t_count
        FROM core_pathaggregation et
        WHERE et.topo_object_id = NEW.topo_object_id;
    IF t_count > 1 THEN
        RETURN NULL;
    END IF;

    -- Deal with newly connected paths
    IF NEW.start_position = 0.0 THEN
        SELECT ST_StartPoint(geom) INTO junction FROM core_path WHERE id = NEW.path_id;
    ELSIF NEW.start_position = 1.0 THEN
        SELECT ST_EndPoint(geom) INTO junction FROM core_path WHERE id = NEW.path_id;
    END IF;

    INSERT INTO core_pathaggregation (path_id, topo_object_id, start_position, end_position)
    SELECT id, NEW.topo_object_id, 0.0, 0.0 -- Troncon departing from this junction
    FROM core_path t
    WHERE id != NEW.path_id AND ST_StartPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM core_pathaggregation WHERE path_id = t.id AND topo_object_id = NEW.topo_object_id
    )
    UNION
    SELECT id, NEW.topo_object_id, 1.0, 1.0-- Troncon arriving at this junction
    FROM core_path t
    WHERE id != NEW.path_id AND ST_EndPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM core_pathaggregation WHERE path_id = t.id AND topo_object_id = NEW.topo_object_id
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql VOLATILE;
-- VOLATILE is the default but I prefer to set it explicitly because it is
-- required for this case (in order to avoid trigger cascading)

CREATE TRIGGER e_r_evenement_troncon_junction_point_iu_tgr
AFTER INSERT OR UPDATE OF start_position, end_position ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_junction_point_iu();
