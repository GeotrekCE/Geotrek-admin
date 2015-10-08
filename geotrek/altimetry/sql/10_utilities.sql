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

CREATE OR REPLACE FUNCTION geotrek.ft_smooth_line(geom geometry)
  RETURNS SETOF geometry AS $$
DECLARE
    current geometry;
    points3d geometry[];
    ele integer;
    last_ele integer;
    last_last_ele integer;
BEGIN
    points3d := ARRAY[]::geometry[];
    ele := NULL;
    last_ele := NULL;
    last_last_ele := NULL;

    FOR current IN SELECT (ST_DumpPoints(ST_Force_3D(geom))).geom AS geom LOOP

         -- smoothing with last element
         ele := (ST_Z(current)::integer + coalesce(last_ele, ST_Z(current)::integer)) / 2;
         points3d := array_append(points3d, ST_MakePoint(ST_X(current), ST_Y(current), ele));

	 last_last_ele := last_ele;
	 last_ele := ele;

    END LOOP;

    RETURN QUERY SELECT (ST_DumpPoints(ST_SetSRID(ST_MakeLine(points3d), ST_SRID(geom)))).geom as geom;

END;

$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION geotrek.ft_smooth_line(
    linegeom geometry,
    step integer)
  RETURNS SETOF geometry AS $$
-- function moving average on altitude lines with specified step

DECLARE

    points geometry[];
    points_output geometry[];
    current_values float;
    val geometry;
    element geometry;
    
BEGIN
    IF step <= 0
    THEN
        RETURN QUERY SELECT * FROM ft_smooth_line(linegeom);
    END IF;

    FOR element in SELECT (ST_DumpPoints(linegeom)).geom LOOP
	points := array_append(points, element);
    END LOOP;

    FOR i IN 0 .. array_length(points, 1) LOOP
        current_values := 0.0;
        
	FOREACH val in ARRAY points[i-step:i+step] LOOP
	    -- val is null when out of array
	    IF val IS NOT NULL
	    THEN
		current_values := current_values + ST_Z(val) / array_length(points[i-step:i+step], 1);
	    END IF;
	END LOOP;
	
	points_output := array_append(points_output, ST_MAKEPOINT(ST_X(points[i]), ST_Y(points[i]), current_values::integer));
    END LOOP;
    
    RETURN QUERY SELECT (ST_DumpPoints(ST_SetSRID(ST_MakeLine(points_output), ST_SRID(linegeom)))).geom as geom;

END;

$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION geotrek.ft_drape_line(linegeom geometry, step integer)
    RETURNS SETOF geometry AS $$
DECLARE
    points geometry[];
BEGIN
    -- Use sampling steps for draping geometry on DEM
    -- http://blog.mathieu-leplatre.info/drape-lines-on-a-dem-with-postgis.html
    -- But make sure to keep original points so 2D geometry and length is preserved
    -- Step is the maximal distance between two points

    IF ST_ZMin(linegeom) < 0 OR ST_ZMax(linegeom) > 0 THEN
        -- Already 3D, do not need to drape.
        -- (Use-case is when assembling paths geometries to build topologies)
        RETURN QUERY SELECT (ST_DumpPoints(ST_Force_3D(ft_smooth_line(linegeom, {{ALTIMETRIC_PROFILE_AVERAGE}})))).geom AS geom;

    ELSE
        
            WITH -- Get endings of each segment of the line
                 r1 AS (SELECT ST_PointN(linegeom, generate_series(1, ST_NPoints(linegeom)-1)) as p1,
                               ST_PointN(linegeom, generate_series(2, ST_NPoints(linegeom))) as p2,
                               generate_series(2, ST_NPoints(linegeom)) = ST_NPoints(linegeom) as is_last),
                 -- Get the number of sub-segments
                 r2 AS (SELECT p1, p2, is_last, trunc(ST_Distance(p1, p2) / step)::integer + 1 AS n FROM r1),
                 -- Get relative positions of new points along the segment (without last point, except for last segment)
                 r3 AS (SELECT p1, p2, generate_series(0, CASE WHEN is_last THEN n ELSE n - 1 END)/n::double precision AS f FROM r2),
                 -- Create new points
                 r4 AS (SELECT ST_MakePoint(ST_X(p1) + (ST_X(p2) - ST_X(p1)) * f,
                                            ST_Y(p1) + (ST_Y(p2) - ST_Y(p1)) * f) as p,
                               ST_SRID(p1) AS srid FROM r3),
                 -- Set SRID of new points
                 r5 AS (SELECT ST_SetSRID(p, srid) as p FROM r4)
            SELECT array_append(points, add_point_elevation(r5.p));
	    RETURN QUERY SELECT (ST_DumpPoints(ST_Force_3D(ft_smooth_line(ST_MAKELINE(points), {{ALTIMETRIC_PROFILE_AVERAGE}})))).geom AS geom;
    END IF;
END;

$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION geotrek.add_point_elevation(geom geometry) RETURNS geometry AS $$
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
        IF NOT FOUND THEN
            ele := 0;
        END IF;
    END IF;

    geom3d := ST_MakePoint(ST_X(geom), ST_Y(geom), ele);
    geom3d := ST_SetSRID(geom3d, ST_SRID(geom));
    RETURN geom3d;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION geotrek.ft_elevation_infos(geom geometry) RETURNS elevation_infos AS $$
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
        ele := ST_Z(current);
        -- Create the 3d points
        points3d := array_append(points3d, current);
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
    IF ST_Length2D(geom) > 0 THEN
        result.slope := (result.max_elevation - result.min_elevation) / ST_Length2D(geom);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION geotrek.ft_elevation_infos(geom geometry, seuil integer) RETURNS elevation_infos AS $$
DECLARE
    num_points integer;
    current geometry;
    points3d geometry[];
    point3d_inflexion geometry[];
    ele integer;
    last_ele integer;
    last_last_ele integer;
    result elevation_infos;
    inflexion_direction boolean;
    previous_geom geometry;
    current_geom geometry;
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

    -- Case of seuil <= 0:
    IF seuil <= 0
    THEN
        SELECT * FROM ft_elevation_infos(geom) INTO result;
        RETURN result;
    END IF;

    -- Now geom is LineString only.

    -- Compute gain and elevation using (higher resolution)
    result.positive_gain := 0;
    result.negative_gain := 0;
    last_ele := NULL;
    last_last_ele := NULL;
    points3d := ARRAY[]::geometry[];
    point3d_inflexion := ARRAY[]::geometry[];
    inflexion_direction := TRUE;
    previous_geom := NULL;
    
    FOR current IN SELECT * FROM ft_drape_line(geom, {{ALTIMETRIC_PROFILE_PRECISION}}) LOOP
        -- Smooth the elevation profile with level minimum
        ele := (ST_Z(current)::integer + coalesce(last_ele, ST_Z(current)::integer)) / 2;

	-- get inflexion points
	IF last_ele IS NULL
	THEN
	    -- first point
            point3d_inflexion := array_append(point3d_inflexion, current);
	ELSIF last_last_ele IS NULL
	THEN
	    -- second point, get inflexion_direction if possible
	    IF ST_Z(current) <> ST_Z(previous_geom)
	    THEN
		inflexion_direction := ST_Z(current) > ST_Z(previous_geom);
	    END IF;
	ELSIF inflexion_direction = TRUE
	THEN
	    -- searching next element lower
	    IF ST_Z(current) < ST_Z(previous_geom)
            THEN
		-- only if seuil respected
	        IF abs(ST_Z(previous_geom) - ST_Z(current)) >= seuil
		THEN
		    point3d_inflexion := array_append(point3d_inflexion, previous_geom);
		END IF;

		-- change inflexion search direction
	        inflexion_direction := FALSE;
            END IF;
	 ELSIF  inflexion_direction = FALSE
	 THEN
	     -- searching next element upper
	     IF ST_Z(current) > ST_Z(previous_geom)
	     THEN
	         IF abs(ST_Z(current) - ST_Z(previous_geom)) >= seuil
		 THEN
		     point3d_inflexion := array_append(point3d_inflexion, previous_geom);
		 END IF;
	                
	         inflexion_direction := TRUE;
	    END IF;
	ELSE
	    -- case of no direction inflexion
	    IF ST_Z(current) <> ST_Z(previous_geom)
	    THEN
		inflexion_direction := ST_Z(current) > ST_Z(previous_geom);
	    END IF;
	END IF;

        -- Create the 3d points
        points3d := array_append(points3d, ST_MakePoint(ST_X(current), ST_Y(current), ele));
        -- Add positive only if ele - last_ele > 0
        --result.positive_gain := result.positive_gain + greatest(ele - coalesce(last_ele, ele), 0);
        -- Add negative only if ele - last_ele < 0
        --result.negative_gain := result.negative_gain + least(ele - coalesce(last_ele, ele), 0);

	last_last_ele := last_ele;
	last_ele := ele;
        previous_geom := current;
        
    END LOOP;

    -- always add last point
    point3d_inflexion := array_append(point3d_inflexion, previous_geom);

    previous_geom := NULL;
    current_geom := NULL;
    
    FOREACH current_geom IN ARRAY point3d_inflexion
    LOOP
		result.positive_gain := result.positive_gain + greatest(ST_Z(current_geom) - coalesce(ST_Z(previous_geom),
																ST_Z(current_geom)), 0);
		result.negative_gain := result.negative_gain + least(ST_Z(current_geom) - coalesce(ST_Z(previous_geom),
															 ST_Z(current_geom)), 0);
		previous_geom := current_geom;
    END LOOP;
    
    result.draped := ST_SetSRID(ST_MakeLine(points3d), ST_SRID(geom));
    --result.points_inflexion := ST_SetSRID(ST_MakeLine(point3d_inflexion, ST_SRID(geom));
    result.min_elevation := ST_ZMin(result.draped)::integer;
    result.max_elevation := ST_ZMax(result.draped)::integer;

    
    -- Compute slope
    result.slope := 0.0;
    
    IF ST_Length2D(geom) > 0 THEN
        result.slope := (result.max_elevation - result.min_elevation) / ST_Length2D(geom);
    END IF;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
