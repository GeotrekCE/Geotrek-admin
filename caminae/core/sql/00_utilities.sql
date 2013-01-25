-------------------------------------------------------------------------------
-- Date trigger functions
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_date_insert() RETURNS trigger AS $$
BEGIN
    NEW.date_insert := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ft_date_update() RETURNS trigger AS $$
BEGIN
    NEW.date_update := statement_timestamp() AT TIME ZONE 'UTC';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Length trigger function
-------------------------------------------------------------------------------

DROP FUNCTION IF EXISTS ft_longueur() CASCADE;

-------------------------------------------------------------------------------
-- Interpolate along : the opposite of ST_LocateAlong
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ST_InterpolateAlong(line geometry, point geometry) RETURNS RECORD AS $$
DECLARE
    linear_offset float;
    shortest_line geometry;
    crossing_dir integer;
    side_offset float;
    tuple record;
BEGIN
    linear_offset := ST_Line_Locate_Point(line, point);
    shortest_line := ST_ShortestLine(line, point);
    crossing_dir := ST_LineCrossingDirection(line, shortest_line);
    -- /!\ In ST_LineCrossingDirection(), offset direction break the convention postive=left/negative=right
    side_offset := ST_Length(shortest_line) * CASE WHEN crossing_dir < 0 THEN 1 WHEN crossing_dir > 0 THEN -1 ELSE 0 END;

    -- Round if close to 0
    IF ABS(side_offset) < 0.1 THEN
        side_offset := 0;
    END IF;

    SELECT linear_offset AS position, side_offset AS distance INTO tuple;
    RETURN tuple;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Check overlapping paths
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION check_path_not_overlap(pid integer, line geometry) RETURNS BOOL AS $$
DECLARE
    t_count integer;
    tolerance float;
BEGIN
    -- Note: I gave up with the idea of checking almost overlap/touch.

    -- tolerance := 1.0;
    -- Crossing and extremity touching is OK. 
    -- Overlapping and --almost overlapping-- is KO.
    SELECT COUNT(*) INTO t_count
    FROM troncons 
    WHERE pid != id 
      AND ST_GeometryType(ST_intersection(geom, line)) IN ('ST_LineString', 'ST_MultiLineString');
      -- not extremity touching
      -- AND ST_Touches(geom, line) = false
      -- not crossing
      -- AND ST_GeometryType(ST_intersection(geom, line)) NOT IN ('ST_Point', 'ST_MultiPoint')
      -- overlap is a line
      -- AND ST_GeometryType(ST_intersection(geom, ST_buffer(line, tolerance))) IN ('ST_LineString', 'ST_MultiLineString')
      -- not almost touching, at most twice
      -- AND       ST_Length(ST_intersection(geom, ST_buffer(line, tolerance))) > (4 * tolerance);
    RETURN t_count = 0;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Convert 2D points and linestring to 3D using a DEM
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION add_point_elevation(geom geometry) RETURNS geometry AS $$
DECLARE
    ele integer;
    geom3d geometry;
BEGIN
    -- Ensure we have a DEM
    PERFORM * FROM raster_columns WHERE r_table_name = 'mnt';
    IF NOT FOUND OR ST_GeometryType(geom) NOT IN ('ST_Point') THEN
        geom3d := ST_MakePoint(ST_X(geom), ST_Y(geom), 0);
        geom3d := ST_SetSRID(geom3d, ST_SRID(geom));
        RETURN geom3d;
    END IF;

    SELECT ST_Value(rast, 1, geom) INTO ele FROM mnt WHERE ST_Intersects(rast, geom);
    IF NOT FOUND THEN
        ele := 0;
    END IF;
    geom3d := ST_MakePoint(ST_X(geom), ST_Y(geom), ele);
    geom3d := ST_SetSRID(geom3d, ST_SRID(geom));
    RETURN geom3d;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION elevation_infos(geom geometry) RETURNS record AS $$
DECLARE
    num_points integer;
    current_point geometry;
    points3d geometry[];
    ele integer;
    last_ele integer;
    max_ele integer;
    min_ele integer;
    positive_gain integer := 0;
    negative_gain integer := 0;
    geom3d geometry;
    result record;
BEGIN
    -- Ensure we have a DEM
    PERFORM * FROM raster_columns WHERE r_table_name = 'mnt';
    IF NOT FOUND THEN
        SELECT ST_Force_3DZ(geom), 0, 0, 0, 0 INTO result;
        RETURN result;
    END IF;

    -- Ensure parameter is a point or a line
    IF ST_GeometryType(geom) NOT IN ('ST_Point', 'ST_LineString') THEN
        SELECT ST_Force_3DZ(geom), 0, 0, 0, 0 INTO result;
        RETURN result;
    END IF;

    -- Obtain point number
    num_points := ST_NPoints(geom); -- /!\ NPoints() works with all types of geom

    -- Iterate over points (i.e. path vertices)
    FOR i IN 1..num_points LOOP
        -- Obtain current point
        IF i = 1 AND ST_GeometryType(geom) = 'ST_Point' THEN
            current_point := geom;
        ELSE
            current_point := ST_PointN(geom, i);
        END IF;

        -- Obtain elevation
        SELECT ST_Value(rast, 1, current_point) INTO ele FROM mnt WHERE ST_Intersects(rast, current_point);
        IF NOT FOUND THEN
            ele := 0;
        END IF;

        -- Store new 3D points
        points3d := array_append(points3d, ST_MakePoint(ST_X(current_point), ST_Y(current_point), ele));

        -- Compute indicators
        min_ele := least(coalesce(min_ele, ele), ele);
        max_ele := greatest(coalesce(max_ele, ele), ele);
        positive_gain := positive_gain + greatest(ele - coalesce(last_ele, ele), 0);
        negative_gain := negative_gain + least(ele - coalesce(last_ele, ele), 0);
        last_ele := ele;
    END LOOP;

    IF ST_GeometryType(geom) = 'ST_Point' THEN
        geom3d := ST_SetSRID(points3d[0], ST_SRID(geom));
    ELSE
        geom3d := ST_SetSRID(ST_MakeLine(points3d), ST_SRID(geom));
    END IF;

    SELECT geom3d, min_ele, max_ele, positive_gain, negative_gain INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Update geometry of an "evenement"
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ST_Smart_Line_Substring(geom geometry, t_start float, t_end float) RETURNS geometry AS $$
DECLARE
    egeom geometry;
BEGIN
    IF t_start < t_end THEN
        egeom := ST_Line_Substring(geom, t_start, t_end);
    ELSE
        egeom := ST_Line_Substring(ST_Reverse(geom), 1.0-t_start, 1.0-t_end);
    END IF;
    RETURN egeom;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION update_geometry_of_evenement(eid integer) RETURNS void AS $$
DECLARE
    egeom geometry;
    lines_only boolean;
    t_count integer;
    t_offset float;

    t_start float;
    t_end float;
    t_geom geometry;
    tomerge geometry[];
BEGIN
    -- See what kind of topology we have
    SELECT bool_and(et.pk_debut != et.pk_fin), count(*)
        INTO lines_only, t_count
        FROM evenements_troncons et
        WHERE et.evenement = eid;

    -- /!\ linear offset (start and end point) are given as a fraction of the
    -- 2D-length in Postgis. Since we are working on 3D geometry, it could lead
    -- to unexpected results.
    -- January 2013 : It does indeed.

    IF t_count = 0 THEN
        -- No more troncons, close this topology
        UPDATE evenements SET geom = ST_GeomFromText('POINTZ EMPTY', 2154), longueur = 0 WHERE id = eid;
    ELSIF NOT lines_only AND t_count = 1 THEN
        -- Special case: the topology describe a point on the path
        -- Note: We are faking a M-geometry in order to use LocateAlong.
        -- This is handy because this function includes an offset parameter
        -- which could be otherwise diffcult to handle.
        SELECT geom, decallage INTO egeom, t_offset FROM evenements e WHERE e.id = eid;
        IF t_offset = 0 OR egeom IS NULL OR ST_IsEmpty(egeom) THEN
            SELECT ST_GeometryN(ST_LocateAlong(ST_AddMeasure(ST_Force_2D(t.geom), 0, 1), et.pk_debut, e.decallage), 1)
                INTO egeom
                FROM evenements e, evenements_troncons et, troncons t
                WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
        END IF;
        UPDATE evenements SET geom = add_point_elevation(egeom), longueur = 0 WHERE id = eid;
    ELSE
        -- Regular case: the topology describe a line

        -- NOTE: LineMerge and Line_Substring work on X and Y only. If two
        -- points in the line have the same X/Y but a different Z, these
        -- functions will see only on point. --> No problem in mountain path management.
        FOR t_start, t_end, t_geom IN SELECT et.pk_debut, et.pk_fin, t.geom
               FROM evenements e, evenements_troncons et, troncons t
               WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id
               ORDER BY et.id  -- /!\ We suppose that evenement_troncons were created in the right order
        LOOP
            tomerge := array_append(tomerge, ST_Smart_Line_Substring(t_geom, t_start, t_end));
        END LOOP;
        egeom := ST_MakeLine(tomerge);
        UPDATE evenements SET geom = ST_Force_3DZ(egeom), longueur = ST_3DLength(egeom) WHERE id = eid;
    END IF;
END;
$$ LANGUAGE plpgsql;
