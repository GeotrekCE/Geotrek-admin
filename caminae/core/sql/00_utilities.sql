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
  tuple RECORD;
BEGIN
    SELECT ST_Line_Locate_Point(line, point) AS position, 
           ST_Distance(point, ST_Line_Interpolate_Point(line, ST_Line_Locate_Point(line, point))) AS offset
    INTO tuple;
    RETURN tuple;
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
        UPDATE evenements SET geom = ST_GeomFromText('POINTZ EMPTY', 2154), longueur = 0, supprime = TRUE WHERE id = eid;
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
        UPDATE evenements SET geom = egeom, longueur = ST_Length(egeom), supprime = FALSE WHERE id = eid;
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
        UPDATE evenements SET geom = egeom, longueur = ST_Length(egeom), supprime = FALSE WHERE id = eid;
    END IF;
END;
$$ LANGUAGE plpgsql;
