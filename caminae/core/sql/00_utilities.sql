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
    RETURN ST_3DDistance(ST_EndPoint(line1), ST_StartPoint(line2)) < 0.1;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION ft_IsAfter(line1 geometry, line2 geometry) RETURNS boolean AS $$
BEGIN
    RETURN ST_3DDistance(ST_StartPoint(line1), ST_EndPoint(line2)) < 0.1;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- A smart ST_MakeLine that will re-oder linestring before merging them
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_Smart_MakeLine(lines geometry[]) RETURNS geometry AS $$
DECLARE
    result geometry;
    t_line geometry;
    remaining int;
    t_found boolean;
BEGIN
    result := ST_GeomFromText('LINESTRINGZ EMPTY');
    remaining := array_length(lines, 1);

    t_found := true;
    WHILE t_found AND remaining > 0
    LOOP
        t_found := false;
        FOREACH t_line IN ARRAY lines 
        LOOP
            IF ST_IsEmpty(result) THEN
                result := t_line;
                t_found := true;
                remaining := remaining-1;
            ELSE
                IF ft_IsAfter(t_line, result) THEN
                    result := ST_MakeLine(result, t_line);
                    t_found := true;
                    remaining := remaining-1;
                ELSEIF ft_IsBefore(t_line, result) THEN
                    result := ST_MakeLine(t_line, result);
                    t_found := true;
                    remaining := remaining-1;
                ELSIF ST_Within(t_line, result) THEN
                    t_found := true;
                    remaining := remaining-1;
                END IF;
            END IF;
        END LOOP;

        IF NOT t_found THEN
            -- Start again, with reversed path if not found
            FOREACH t_line IN ARRAY lines 
            LOOP
                t_line := ST_Reverse(t_line);
                IF ft_IsAfter(t_line, result) THEN
                    result := ST_MakeLine(result, t_line);
                    t_found := true;
                    remaining := remaining-1;
                ELSEIF ft_IsBefore(t_line, result) THEN
                    result := ST_MakeLine(t_line, result);
                    t_found := true;
                    remaining := remaining-1;
                ELSIF ST_Within(t_line, result) THEN
                    t_found := true;
                    remaining := remaining-1;
                END IF;
            END LOOP;
        END IF;
    END LOOP;
    IF NOT t_found THEN
        -- RAISE WARNING 'Cannot connect Topology paths: %', ST_AsText(ST_MakeLine(lines));
        result := ST_MakeLine(lines);
    END IF;
    -- RAISE NOTICE 'Merged % into %', ST_AsText(ST_Union(lines)), ST_AsText(result);
    RETURN result;
END;
$$ LANGUAGE plpgsql;

