-------------------------------------------------------------------------------
-- Interpolate along : the opposite of ST_LocateAlong
-------------------------------------------------------------------------------

CREATE TYPE {{ schema_geotrek }}.line_infos AS
(
    new_geometry
    geometry,
    new_order
    integer
[]
);

CREATE OR REPLACE FUNCTION st_line_extend(  -- Backport of ST_LineExtend from PostGIS 3.4
    geom geometry,
    head_constant double precision,
    tail_constant double precision)
    RETURNS geometry AS
$BODY$
    -- Extends a linestring.
-- First segment get extended by length + head_constant.
-- Last segment get extended by length + tail_constant.
--
-- References:
-- http://blog.cleverelephant.ca/2015/02/breaking-linestring-into-segments.html
-- https://gis.stackexchange.com/a/104451/44921
-- https://gis.stackexchange.com/a/16701/44921
WITH segment_parts AS (
    SELECT (pt).path[1] - 1 as segment_num,
        CASE WHEN (nth_value((pt).path, 2) OVER ()) = (pt).path AND (last_value((pt).path) OVER ()) = (pt).path
            THEN 3
            WHEN (nth_value((pt).path, 2) OVER ()) = (pt).path
            THEN 1
            WHEN (last_value((pt).path) OVER ()) = (pt).path
            THEN 2
            ELSE 0
        END AS segment_flag,
        (pt).geom AS a,
        lag((pt).geom, 1, NULL) OVER () AS b
    FROM ST_DumpPoints($1) pt
), extended_segment_parts AS (
    SELECT *,
           ST_Azimuth(a, b)  AS az1,
           ST_Azimuth(b, a)  AS az2,
           ST_Distance(a, b) AS len
    FROM segment_parts
    WHERE b IS NOT NULL
), expanded_segment_parts AS (
    SELECT segment_num,
         CASE
             WHEN bool(segment_flag & 2)
             THEN ST_Translate(b, sin(az2) * (len + tail_constant),
                               cos(az2) * (len + tail_constant))
             ELSE
                 a
        END AS a,
        CASE WHEN bool(segment_flag & 1)
             THEN ST_Translate(a, sin(az1) * (len + head_constant),
                               cos(az1) * (len + head_constant))
             ELSE b
        END AS b
    FROM extended_segment_parts
), expanded_segment_lines AS (
    SELECT segment_num,
           ST_MakeLine(b, a) as geom
    FROM expanded_segment_parts
)
SELECT ST_LineMerge(ST_Collect(geom ORDER BY segment_num)) AS geom
FROM expanded_segment_lines;

$BODY$
    LANGUAGE sql;

CREATE FUNCTION {{ schema_geotrek }}.ST_InterpolateAlong(line geometry, point geometry) RETURNS RECORD AS
$$
DECLARE
    linear_offset float;
    shortest_line geometry;
    crossing_dir integer;
    side_offset float;
    tuple record;
BEGIN
    linear_offset := ST_LineLocatePoint(line, point);
    shortest_line := ST_ShortestLine(line, point);
    crossing_dir := ST_LineCrossingDirection(line, st_line_extend(shortest_line, 2, 2));
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
-- A smart ST_LineSubstring that supports start > end
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.ST_SmartLineSubstring(geom geometry, t_start float, t_end float) RETURNS geometry AS
$$
DECLARE
    egeom geometry;
BEGIN
    IF t_start < t_end THEN
        egeom := ST_LineSubstring(geom, t_start, t_end);
    ELSE
        egeom := ST_LineSubstring(ST_Reverse(geom), 1.0-t_start, 1.0-t_end);
    END IF;
    RETURN egeom;
END;

$$ LANGUAGE plpgsql;


CREATE FUNCTION {{ schema_geotrek }}.ft_IsBefore(line1 geometry, line2 geometry) RETURNS boolean AS
$$
BEGIN
    RETURN ST_Distance(ST_EndPoint(line1), ST_StartPoint(line2)) < 1;
END;

$$ LANGUAGE plpgsql;


CREATE FUNCTION {{ schema_geotrek }}.ft_IsAfter(line1 geometry, line2 geometry) RETURNS boolean AS
$$
BEGIN
    RETURN ST_Distance(ST_StartPoint(line1), ST_EndPoint(line2)) < 1;
END;

$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- A smart ST_MakeLine that will re-oder linestring before merging them
-------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.ft_Smart_MakeLine(lines geometry[]) RETURNS line_infos AS
$$
DECLARE
    result geometry;
    t_line geometry;
    nblines int;
    current int[];
    i int;
    t_proceed boolean;
    t_found boolean;
    final_result line_infos;
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
        -- RAISE NOTICE 'Cannot connect Topology paths: %', ST_AsText(ST_Union(lines));
        current := ARRAY[]::integer[];
    END IF;
    result := ST_SetSRID(result, ST_SRID(lines[1]));
    final_result.new_geometry = result;
    final_result.new_order = current;
    RETURN final_result;
END;

$$ LANGUAGE plpgsql;


----------------------------------------------------------------------------------------------------------
-- Returns whether a topology is valid or not. See https://github.com/GeotrekCE/Geotrek-admin/issues/4982
----------------------------------------------------------------------------------------------------------

CREATE FUNCTION {{ schema_geotrek }}.TopologyIsValid(topology_id integer) RETURNS boolean AS
$$
DECLARE
    agg_count INTEGER;
    is_point_topology BOOLEAN;
    distinct_order_count INTEGER;
    prev_path_id INTEGER;
    agg_record RECORD;
    current_point GEOMETRY;
    prev_point GEOMETRY;
BEGIN
    -- A linear topology is valid if:
    --     - its path aggregations don't contain duplicates (on the "order" column)
    --     - its path aggregations are in the correct order and direction

    -- Get the number of aggregations corresponding to this topology
    SELECT COUNT(*) INTO agg_count
    FROM core_pathaggregation
    WHERE topo_object_id = topology_id;

    -- Edge case: topology with no aggregations (decoupled from the network, but still valid)
    IF agg_count = 0 THEN
        RETURN TRUE;
    END IF;

    -- Edge case: point topology (all aggregations have start_position == end_position)
    SELECT COUNT(*) = 0 INTO is_point_topology
    FROM core_pathaggregation
    WHERE topo_object_id = topology_id
    AND start_position != end_position;

    IF is_point_topology THEN
        RETURN TRUE;
    END IF;

    -- Check that there are no duplicate orders
    SELECT COUNT(DISTINCT "order") INTO distinct_order_count
    FROM core_pathaggregation
    WHERE topo_object_id = topology_id;

    IF distinct_order_count != agg_count THEN
        RETURN FALSE;
    END IF;

    -- Check the sequential connectivity
    prev_path_id := NULL;

    -- Loop on all aggregations for this topology
    FOR agg_record IN
        SELECT cpa.path_id, cpa.start_position, cpa.end_position, cp.geom
        FROM core_pathaggregation cpa
        JOIN core_path cp ON cpa.path_id = cp.id
        WHERE cpa.topo_object_id = topology_id
        ORDER BY cpa."order"
    LOOP
        -- Get the geometric point where this aggregation starts
        current_point := ST_LineInterpolatePoint(agg_record.geom, agg_record.start_position);

        -- Check that this aggregation starts where the previous one ended
        IF prev_path_id IS NOT NULL THEN
            IF NOT ST_Equals(prev_point, current_point) THEN
                RETURN FALSE;
            END IF;
        END IF;

        -- Store where this aggregation ends for the next iteration
        prev_point := ST_LineInterpolatePoint(agg_record.geom, agg_record.end_position);
        prev_path_id := agg_record.path_id;
    END LOOP;

    RETURN TRUE;
END;

$$ LANGUAGE plpgsql;
