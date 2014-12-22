-------------------------------------------------------------------------------
-- Interpolate along : the opposite of ST_LocateAlong
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.ST_InterpolateAlong(line geometry, point geometry) RETURNS RECORD AS $$
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
-- A smart ST_Line_Substring that supports start > end
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.ST_Smart_Line_Substring(geom geometry, t_start float, t_end float) RETURNS geometry AS $$
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


CREATE OR REPLACE FUNCTION geotrek.ft_IsBefore(line1 geometry, line2 geometry) RETURNS boolean AS $$
BEGIN
    RETURN ST_Distance(ST_EndPoint(line1), ST_StartPoint(line2)) < 1;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION geotrek.ft_IsAfter(line1 geometry, line2 geometry) RETURNS boolean AS $$
BEGIN
    RETURN ST_Distance(ST_StartPoint(line1), ST_EndPoint(line2)) < 1;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- A smart ST_MakeLine that will re-oder linestring before merging them
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.ft_Smart_MakeLine(lines geometry[]) RETURNS geometry AS $$
DECLARE
    result geometry;
    t_line geometry;
    nblines int;
    current int[];
    i int;
    t_proceed boolean;
    t_found boolean;
BEGIN
    result := ST_GeomFromText('LINESTRING EMPTY');
    nblines := array_length(lines, 1);
    current := array_append(current, 0);
    t_found := true;
    WHILE t_found AND array_length(current, 1) < nblines + 1
    LOOP
        t_found := false;
        i := 1;
        WHILE i < nblines + 1
        LOOP
            t_proceed := NOT current @> ARRAY[i];
            t_line := lines[i];
            IF ST_IsEmpty(result) THEN
                result := t_line;
                t_found := true;
                current := array_append(current, i);
            ELSIF t_proceed THEN
                IF ft_IsAfter(t_line, result) THEN
                    result := ST_MakeLine(result, t_line);
                    t_found := true;
                    current := array_append(current, i);
                    i := 0;  -- restart iteration
                ELSEIF ft_IsBefore(t_line, result) THEN
                    result := ST_MakeLine(t_line, result);
                    t_found := true;
                    current := array_append(current, i);
                    i := 0;  -- restart iteration
                END IF;

                IF NOT t_found THEN
                    t_line := ST_Reverse(t_line);
                    IF ft_IsAfter(t_line, result) THEN
                        result := ST_MakeLine(result, t_line);
                        t_found := true;
                        current := array_append(current, i);
                    ELSEIF ft_IsBefore(t_line, result) THEN
                        result := ST_MakeLine(t_line, result);
                        t_found := true;
                        current := array_append(current, i);
                    END IF;
                END IF;
            END IF;

            i := i + 1;
        END LOOP;
    END LOOP;

    IF NOT t_found THEN
        result := ST_Union(lines);
        RAISE NOTICE 'Cannot connect Topology paths: %', ST_AsText(ST_Union(lines));
    END IF;
    result := ST_SetSRID(result, ST_SRID(lines[1]));
    RETURN result;
END;
$$ LANGUAGE plpgsql;

