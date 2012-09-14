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
    shortest_line := ST_3DShortestLine(line, point);
    crossing_dir := ST_LineCrossingDirection(line, shortest_line);
    -- /!\ In ST_LineCrossingDirection(), offset direction break the convention postive=left/negative=right
    side_offset := ST_Length(shortest_line) * CASE WHEN crossing_dir < 0 THEN 1 WHEN crossing_dir > 0 THEN -1 ELSE 0 END;

    SELECT linear_offset AS position, side_offset AS distance INTO tuple;
    RETURN tuple;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Convert 2D linestring to 3D using a DEM
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION add_elevation(geom geometry) RETURNS record AS $$
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

CREATE OR REPLACE FUNCTION update_geometry_of_evenement(eid integer) RETURNS void AS $$
DECLARE
    egeom geometry;
    lines_only boolean;
    t_count integer;
BEGIN
    -- See what kind of topology we have
    SELECT bool_and(et.pk_debut != et.pk_fin), count(*)
        INTO lines_only, t_count
        FROM evenements_troncons et
        WHERE et.evenement = eid;

    IF t_count = 0 THEN
        -- No more troncons, close this topology
        UPDATE evenements SET geom = ST_GeomFromText('POINTZ EMPTY', 2154), longueur = 0 WHERE id = eid;
    ELSIF NOT lines_only AND t_count > 1 THEN
        -- FIXME: This is an invalid case (a multi-point topology or a
        -- mixed points/lines topology), how to handle it?
    ELSIF NOT lines_only AND t_count = 1 THEN
        -- Special case: the topology describe a point on the path
        -- Note: We are faking a M-geometry in order to use LocateAlong.
        -- This is handy because this function includes an offset parameter
        -- which could be otherwise diffcult to handle.
        SELECT ST_Force_3DZ(ST_GeometryN(ST_LocateAlong(ST_AddMeasure(t.geom, 0, 1), et.pk_debut, e.decallage), 1))
            INTO egeom
            FROM evenements e, evenements_troncons et, troncons t
            WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id;
        UPDATE evenements SET geom = egeom, longueur = ST_Length(egeom) WHERE id = eid;
    ELSE
        -- Regular case: the topology describe a line
        -- Note: We are faking a M-geometry in order to use LocateBetween
        -- which is better than OffsetCurve because it will not drop the
        -- Z-index.
        -- FIXME: If paths are not contiguous, only the first chunk will be
        -- considered. How to handle these invalid linear topologies?
        SELECT ST_Force_3DZ(ST_GeometryN(ST_LocateBetween(ST_AddMeasure(ST_LineMerge(ST_Collect(ST_Line_Substring(t.geom, et.pk_debut, et.pk_fin))), 0, 1), 0, 1, e.decallage), 1))
            INTO egeom
            FROM evenements e, evenements_troncons et, troncons t
            WHERE e.id = eid AND et.evenement = e.id AND et.troncon = t.id
            GROUP BY e.id, e.decallage;
        UPDATE evenements SET geom = egeom, longueur = ST_Length(egeom) WHERE id = eid;
    END IF;
END;
$$ LANGUAGE plpgsql;
