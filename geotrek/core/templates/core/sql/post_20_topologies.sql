ALTER TABLE core_topology DROP CONSTRAINT IF EXISTS e_t_evenement_geom_not_empty;
ALTER TABLE core_topology DROP CONSTRAINT IF EXISTS core_topology_geom_not_empty;


-------------------------------------------------------------------------------
-- Keep dates up-to-date
-------------------------------------------------------------------------------

CREATE TRIGGER core_topology_date_insert_tgr
    BEFORE INSERT ON core_topology
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

CREATE TRIGGER core_topology_date_update_tgr
    BEFORE INSERT OR UPDATE ON core_topology
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

---------------------------------------------------------------------
-- Make sure cache key (base on lastest updated) is refresh on DELETE
---------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.topology_latest_updated_d() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
BEGIN
    insert into trigger_count (trigger_id, count_trigger, created_at) VALUES('topology_latest_updated_d', pg_trigger_depth(), clock_timestamp());
    -- Touch latest path
    UPDATE core_topology SET date_update = NOW()
    WHERE id IN (SELECT id FROM core_topology ORDER BY date_update DESC LIMIT 1);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_topology_latest_updated_d_tgr
AFTER DELETE ON core_topology
FOR EACH ROW EXECUTE PROCEDURE topology_latest_updated_d();


-------------------------------------------------------------------------------
-- Update geometry of a topology
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.update_geometry_of_topology(topology_id integer) RETURNS void AS $$
DECLARE
    egeom geometry;
    egeom_3d geometry;
    lines_only boolean;
    points_only boolean;
    position_point float;
    elevation elevation_infos;
    t_count integer;
    t_offset float;

    t_start float;
    t_end float;
    t_geom geometry;
    t_geom_3d geometry;
    tomerge geometry[];
    tomerge_3d geometry[];

    smart_makeline line_infos;
    smart_makeline_3d line_infos;
BEGIN
    insert into trigger_count (trigger_id, count_trigger, created_at) VALUES('update_geometry_of_topology', pg_trigger_depth(), clock_timestamp());
    -- If Geotrek-light, don't do anything
    IF NOT {{ TREKKING_TOPOLOGY_ENABLED }} THEN
        RETURN;
    END IF;

    -- See what kind of topology we have
    SELECT bool_and(et.start_position != et.end_position), bool_and(et.start_position = et.end_position), count(*)
        INTO lines_only, points_only, t_count
        FROM core_pathaggregation et
        WHERE et.topo_object_id = topology_id;

    -- /!\ linear offset (start and end point) are given as a fraction of the
    -- 2D-length in Postgis. Since we are working on 3D geometry, it could lead
    -- to unexpected results.
    -- January 2013 : It does indeed.

    -- RAISE NOTICE 'update_geometry_of_topology (lines_only:% points_only:% t_count:%)', lines_only, points_only, t_count;

    IF t_count = 0 THEN
        -- No more paths, close this topology
        UPDATE core_topology SET deleted = true, geom = NULL, "length" = 0 WHERE id = topology_id;
    ELSIF (NOT lines_only AND t_count = 1) OR points_only THEN
        -- Special case: the topology describe a point on the path
        -- Note: We are faking a M-geometry in order to use LocateAlong.
        -- This is handy because this function includes an offset parameter
        -- which could be otherwise diffcult to handle.
        SELECT geom, "offset" INTO egeom, t_offset FROM core_topology e WHERE e.id = topology_id;
        -- RAISE NOTICE '% % % %', (t_offset = 0), (egeom IS NULL), (ST_IsEmpty(egeom)), (ST_X(egeom) = 0 AND ST_Y(egeom) = 0);
        IF t_offset = 0 OR egeom IS NULL OR ST_IsEmpty(egeom) OR (ST_X(egeom) = 0 AND ST_Y(egeom) = 0) THEN
            -- ST_LocateAlong can give no point when we try to get the startpoint or the endpoint of the line
            SELECT et.start_position INTO position_point FROM core_pathaggregation et WHERE et.topo_object_id = topology_id;
            IF (position_point < 0.000000000000001) THEN
                SELECT ST_StartPoint(t.geom) INTO egeom
                FROM core_topology e, core_pathaggregation et, core_path t
                WHERE e.id = topology_id AND et.topo_object_id = e.id AND et.path_id = t.id;
            ELSIF (position_point > 0.999999999999999) THEN
                SELECT ST_EndPoint(t.geom) INTO egeom
                FROM core_topology e, core_pathaggregation et, core_path t
                WHERE e.id = topology_id AND et.topo_object_id = e.id AND et.path_id = t.id;
            ELSE
                SELECT ST_GeometryN(ST_LocateAlong(ST_AddMeasure(ST_Force2D(t.geom), 0, 1), et.start_position, e.offset), 1)
                    INTO egeom
                    FROM core_topology e, core_pathaggregation et, core_path t
                    WHERE e.id = topology_id AND et.topo_object_id = e.id AND et.path_id = t.id;
            END IF;
        END IF;

        egeom_3d := egeom;
    ELSE
        -- Regular case: the topology describe a line
        -- NOTE: LineMerge and Line_Substring work on X and Y only. If two
        -- points in the line have the same X/Y but a different Z, these
        -- functions will see only on point. --> No problem in mountain path management.
        FOR t_offset, t_geom, t_geom_3d IN SELECT e."offset", ST_SmartLineSubstring(t.geom, et.start_position, et.end_position),
                                                               ST_SmartLineSubstring(t.geom_3d, et.start_position, et.end_position)
               FROM core_topology e, core_pathaggregation et, core_path t
               WHERE e.id = topology_id AND et.topo_object_id = e.id AND et.path_id = t.id
                 AND GeometryType(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position)) != 'POINT'
               ORDER BY et."order", et.id  -- /!\ We suppose that path aggregations were created in the right order
        LOOP
            tomerge := array_append(tomerge, t_geom);
            tomerge_3d := array_append(tomerge_3d, t_geom_3d);
        END LOOP;
        SELECT * FROM ft_Smart_MakeLine(tomerge) INTO smart_makeline;
        SELECT * FROM ft_Smart_MakeLine(tomerge_3d) INTO smart_makeline_3d;
        egeom := smart_makeline.new_geometry;
        egeom_3d := smart_makeline_3d.new_geometry;
        -- Add some offset if necessary.
        IF t_offset != 0 THEN
            egeom := ST_GeometryN(ST_LocateBetween(ST_AddMeasure(egeom, 0, 1), 0, 1, t_offset), 1);
            egeom_3d := ST_GeometryN(ST_LocateBetween(ST_AddMeasure(egeom_3d, 0, 1), 0, 1, t_offset), 1);
        END IF;
    END IF;

    IF t_count > 0 THEN
        SELECT * FROM ft_elevation_infos(egeom_3d, {{ ALTIMETRIC_PROFILE_STEP }}) INTO elevation;
        UPDATE core_topology SET geom = ST_Force2D(egeom),
                                 geom_3d = ST_Force3DZ(elevation.draped),
                                 "length" = ST_3DLength(elevation.draped),
                                 slope = elevation.slope,
                                 min_elevation = elevation.min_elevation,
                                 max_elevation = elevation.max_elevation,
                                 ascent = elevation.positive_gain,
                                 descent = elevation.negative_gain
                             WHERE id = topology_id;
    END IF;
    UPDATE core_topology SET geom_need_update = FALSE WHERE id = topology_id;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Update geometry when offset change
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.update_topology_geom_when_offset_changes() RETURNS trigger SECURITY DEFINER AS $$
BEGIN
    insert into trigger_count (trigger_id, count_trigger, created_at) VALUES('update_topology_geom_when_offset_changes', pg_trigger_depth(), clock_timestamp());
    -- Note: We are using an "after" trigger here because the function below
    -- takes topology id as an argument and emits its own SQL queries to read
    -- and write data.
    -- Since the topology to be modified is available in NEW, we could improve
    -- performance with some refactoring.

    PERFORM update_geometry_of_topology(NEW.id);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_topology_offset_u_tgr
AFTER UPDATE OF "offset" ON core_topology
FOR EACH ROW
WHEN (NEW.kind != 'TMP' AND (NEW.geom_3d IS NULL OR OLD.offset != NEW.offset))
EXECUTE PROCEDURE update_topology_geom_when_offset_changes();

-------------------------------------------------------------------------------
-- Update altimetry when geom change (Geotrek-light)
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.topology_elevation_iu() RETURNS trigger SECURITY DEFINER AS $$
DECLARE
    elevation elevation_infos;
BEGIN
    insert into trigger_count (trigger_id, count_trigger, created_at) VALUES('topology_elevation_iu', pg_trigger_depth(), clock_timestamp());
    IF {{ TREKKING_TOPOLOGY_ENABLED }} THEN
        RETURN NEW;
    END IF;
    SELECT * FROM ft_elevation_infos(NEW.geom, {{ ALTIMETRIC_PROFILE_STEP }}) INTO elevation;
    -- Update path geometry
    NEW.geom_3d := elevation.draped;
    NEW."length" := ST_3DLength(elevation.draped);
    NEW.slope := elevation.slope;
    NEW.min_elevation := elevation.min_elevation;
    NEW.max_elevation := elevation.max_elevation;
    NEW.ascent := elevation.positive_gain;
    NEW.descent := elevation.negative_gain;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER core_topology_geom_iu_tgr
BEFORE INSERT OR UPDATE OF geom ON core_topology
FOR EACH ROW EXECUTE PROCEDURE topology_elevation_iu();
