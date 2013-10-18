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
    side_offset := ST_Length(shortest_line) * CASE WHEN crossing_dir <= 0
                                                   THEN 1
                                                   ELSE -1 END;

    -- Round if close to 0
    IF ABS(side_offset) < 0.1 THEN
        side_offset := 0;
    END IF;

    SELECT linear_offset AS position, side_offset AS distance INTO tuple;
    RETURN tuple;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Convert 2D to 3D using a DEM
-------------------------------------------------------------------------------

DROP TYPE IF EXISTS elevation_infos CASCADE;
CREATE TYPE elevation_infos AS (
    draped geometry,
    slope float,
    min_elevation integer,
    max_elevation integer,
    positive_gain integer,
    negative_gain integer
);


DROP FUNCTION IF EXISTS ft_drape_line(geometry, integer);
CREATE OR REPLACE FUNCTION ft_drape_line(linegeom geometry, step integer)
    RETURNS SETOF geometry AS $$
DECLARE
    length float;
BEGIN
    -- Use sampling steps for draping geometry on DEM
    -- http://blog.mathieu-leplatre.info/drape-lines-on-a-dem-with-postgis.html

    length := ST_Length(linegeom);

    IF ST_ZMin(linegeom) > 0 THEN
        -- Already 3D, do not need to drape.
        -- (Use-case is when assembling paths geometries to build topologies)
        RETURN QUERY SELECT (ST_DumpPoints(ST_Force_3D(linegeom))).geom AS geom;

    ELSIF length < step THEN
        RETURN QUERY SELECT add_point_elevation((ST_DumpPoints(linegeom)).geom);

    ELSE
        RETURN QUERY
            WITH linemesure AS
                 -- Add a mesure dimension to extract steps
                   (SELECT ST_AddMeasure(linegeom, 0, length) as linem,
                           generate_series(step, length::int, step) as i),
                 points2d AS
                   (SELECT 0 as distance, ST_StartPoint(linegeom) as geom
                    UNION
                    SELECT i as distance, ST_GeometryN(ST_LocateAlong(linem, i), 1) AS geom FROM linemesure
                    UNION
                    SELECT length as distance, ST_EndPoint(linegeom) as geom)
            SELECT add_point_elevation(p.geom)
            FROM points2d p
            ORDER BY p.distance;
    END IF;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION add_point_elevation(geom geometry) RETURNS geometry AS $$
DECLARE
    ele integer;
    geom3d geometry;
BEGIN
    ele := coalesce(ST_Z(geom)::integer, 0);
    IF ele > 0 THEN
        RETURN geom;
    END IF;

    -- Ensure we have a DEM
    PERFORM * FROM raster_columns WHERE r_table_name = 'mnt';
    IF FOUND THEN
        SELECT ST_Value(rast, 1, geom)::integer INTO ele
        FROM mnt
        WHERE ST_Intersects(rast, geom);
    END IF;

    geom3d := ST_MakePoint(ST_X(geom), ST_Y(geom), ele);
    geom3d := ST_SetSRID(geom3d, ST_SRID(geom));
    RETURN geom3d;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ft_elevation_infos(geom geometry) RETURNS elevation_infos AS $$
DECLARE
    num_points integer;
    current geometry;
    points3d geometry[];
    ele integer;
    last_ele integer;
    result elevation_infos;
BEGIN
    -- Skip if no DEM (speed-up tests)
    PERFORM * FROM raster_columns WHERE r_table_name = 'mnt';
    IF NOT FOUND THEN
        SELECT ST_Force_3DZ(geom), 0.0, 0, 0, 0, 0 INTO result;
        RETURN result;
    END IF;

    -- Ensure parameter is a point or a line
    IF ST_GeometryType(geom) NOT IN ('ST_Point', 'ST_LineString') THEN
        SELECT ST_Force_3DZ(geom), 0.0, 0, 0, 0, 0 INTO result;
        RETURN result;
    END IF;

    -- Specific case for points
    IF ST_GeometryType(geom) = 'ST_Point' THEN
        current := add_point_elevation(geom);
        SELECT current, 0.0, ST_Z(current), ST_Z(current), 0, 0 INTO result;
        RETURN result;
    END IF;

    -- Now geom is LineString only.

    -- Compute gain and elevation using (higher resolution)
    result.positive_gain := 0;
    result.negative_gain := 0;
    last_ele := NULL;
    points3d := ARRAY[]::geometry[];

    FOR current IN SELECT * FROM ft_drape_line(geom, {{ALTIMETRIC_PROFILE_PRECISION}}) LOOP
        points3d := array_append(points3d, current);
        ele := ST_Z(current)::integer;
        -- Add positive only if ele - last_ele > 0
        result.positive_gain := result.positive_gain + greatest(ele - coalesce(last_ele, ele), 0);
        -- Add negative only if ele - last_ele < 0
        result.negative_gain := result.negative_gain + least(ele - coalesce(last_ele, ele), 0);
        last_ele := ele;
    END LOOP;
    result.draped := ST_SetSRID(ST_MakeLine(points3d), ST_SRID(geom));

    result.min_elevation := ST_ZMin(result.draped)::integer;
    result.max_elevation := ST_ZMax(result.draped)::integer;

    -- Compute slope
    result.slope := 0.0;
    IF ST_Length2D(result.draped) > 0 THEN
        result.slope := (result.max_elevation - result.min_elevation) / ST_Length2D(geom);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- A smart ST_Line_Substring that supports start > end
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


CREATE OR REPLACE FUNCTION ft_IsBefore(line1 geometry, line2 geometry) RETURNS boolean AS $$
BEGIN
    RETURN ST_Distance(ST_EndPoint(line1), ST_StartPoint(line2)) < 1;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ft_IsAfter(line1 geometry, line2 geometry) RETURNS boolean AS $$
BEGIN
    RETURN ST_Distance(ST_StartPoint(line1), ST_EndPoint(line2)) < 1;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- A smart ST_MakeLine that will re-oder linestring before merging them
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_Smart_MakeLine(lines geometry[]) RETURNS geometry AS $$
DECLARE
    result geometry;
    t_line geometry;
    nblines int;
    current int[];
    i int;
    t_proceed boolean;
    t_found boolean;
    t_failed boolean;
BEGIN
    result := ST_GeomFromText('LINESTRING EMPTY');
    nblines := array_length(lines, 1);
    current := array_append(current, 0);
    t_found := true;
    WHILE t_found AND array_length(current, 1) < nblines + 1
    LOOP
        t_found := false;
        FOR i IN 1 .. nblines
        LOOP
            t_proceed := NOT current @> ARRAY[i];
            t_line := lines[i];
            IF ST_IsEmpty(result) THEN
                result := t_line;
                t_found := true;
                current := array_append(current, i);
            ELSE
                IF t_proceed AND ft_IsAfter(t_line, result) THEN
                    result := ST_MakeLine(result, t_line);
                    t_found := true;
                    current := array_append(current, i);
                ELSEIF t_proceed AND ft_IsBefore(t_line, result) THEN
                    result := ST_MakeLine(t_line, result);
                    t_found := true;
                    current := array_append(current, i);
                END IF;

                IF NOT t_found THEN
                    t_line := ST_Reverse(t_line);
                    IF t_proceed AND ft_IsAfter(t_line, result) THEN
                        result := ST_MakeLine(result, t_line);
                        t_found := true;
                        current := array_append(current, i);
                    ELSEIF t_proceed AND ft_IsBefore(t_line, result) THEN
                        result := ST_MakeLine(t_line, result);
                        t_found := true;
                        current := array_append(current, i);
                    END IF;
                END IF;

            END IF;
        END LOOP;
    END LOOP;

    t_failed := ST_Length(result) < ST_Length(ST_Union(lines));
    IF NOT t_found OR t_failed THEN
        result := ST_Union(lines);
        RAISE NOTICE 'Cannot connect Topology paths: %', ST_AsText(ST_Union(lines));
    ELSE
        result := ST_SetSRID(result, ST_SRID(lines[1]));
    END IF;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

