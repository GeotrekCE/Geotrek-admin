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
    last_last_ele integer;
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
    last_last_ele := NULL;
    points3d := ARRAY[]::geometry[];

    FOR current IN SELECT * FROM ft_drape_line(geom, {{ALTIMETRIC_PROFILE_PRECISION}}) LOOP
        -- Smooth the elevation profile
        ele := (ST_Z(current)::integer + coalesce(last_ele, ST_Z(current)::integer)) / 2;
        -- Create the 3d points
        points3d := array_append(points3d, ST_MakePoint(ST_X(current), ST_Y(current), ele));
        -- Add positive only if ele - last_ele > 0
        result.positive_gain := result.positive_gain + greatest(ele - coalesce(last_ele, ele), 0);
        -- Add negative only if ele - last_ele < 0
        result.negative_gain := result.negative_gain + least(ele - coalesce(last_ele, ele), 0);
        last_ele := ele;
        last_last_ele := last_ele;
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
