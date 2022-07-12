-------------------------------------------------------------------------------
-- Alter FK to path in order to add CASCADE behavior at DB-level
-------------------------------------------------------------------------------

DO LANGUAGE plpgsql $$
DECLARE
    row record;
BEGIN
    -- Obtain FK name (which is dynamically generated when table is created)
    -- Use loop to delete all FK generated in previous migrate (bug fix)
    FOR row IN SELECT c.conname
               FROM pg_class t1, pg_class t2, pg_constraint c
               WHERE t1.relname = 'core_pathaggregation' AND c.conrelid = t1.oid
                 AND t2.relname = 'core_path' AND c.confrelid = t2.oid
                 AND c.contype = 'f'
    -- Use a dynamic SQL statement with the name found
    LOOP
        EXECUTE 'ALTER TABLE core_pathaggregation DROP CONSTRAINT IF EXISTS ' || quote_ident(row.conname);
    END LOOP;
END;
$$;

-- Now re-create the FK with cascade option
ALTER TABLE core_pathaggregation ADD FOREIGN KEY (path_id) REFERENCES core_path(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


-------------------------------------------------------------------------------
-- Evenements utilities
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.ft_path_interpolate(path integer, point geometry) RETURNS RECORD AS $$
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

CREATE FUNCTION {{ schema_geotrek }}.ft_topologies_paths_geometry() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE core_topology SET geom_need_update = TRUE WHERE id = NEW.topo_object_id AND kind != 'TMP';
    ELSE
        UPDATE core_topology SET geom_need_update = TRUE WHERE id = OLD.topo_object_id AND kind != 'TMP';
        IF TG_OP = 'UPDATE' THEN -- /!\ Logical ops are commutative in SQL
            IF NEW.topo_object_id != OLD.topo_object_id THEN
                UPDATE core_topology SET geom_need_update = TRUE WHERE id = NEW.topo_object_id AND kind != 'TMP';
            END IF;
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_pathaggregation_geometry_tgr
AFTER INSERT OR UPDATE OR DELETE ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE ft_topologies_paths_geometry();


DROP TRIGGER IF EXISTS core_pathaggregation_geometry_statement_tgr ON core_pathaggregation;
DROP FUNCTION IF EXISTS ft_topologies_paths_geometry_statement() CASCADE;

CREATE FUNCTION {{ schema_geotrek }}.ft_topologies_paths_geometry_statement() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    rec record;
BEGIN
    FOR rec IN SELECT * FROM core_topology WHERE geom_need_update = TRUE LOOP
        PERFORM update_geometry_of_topology(rec.id);
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_pathaggregation_geometry_statement_tgr
AFTER INSERT OR UPDATE OR DELETE ON core_pathaggregation
FOR EACH STATEMENT EXECUTE PROCEDURE ft_topologies_paths_geometry_statement();


-------------------------------------------------------------------------------
-- Emulate junction points
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.ft_topologies_paths_junction_point_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    junction geometry;
    t_count integer;
BEGIN
    -- Deal with previously connected paths in the case of an UPDATE action
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
    -- is not the only path aggregation, then it's an intermediate marker.
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

CREATE TRIGGER core_pathaggregation_junction_point_iu_tgr
AFTER INSERT OR UPDATE OF start_position, end_position ON core_pathaggregation
FOR EACH ROW EXECUTE PROCEDURE ft_topologies_paths_junction_point_iu();
