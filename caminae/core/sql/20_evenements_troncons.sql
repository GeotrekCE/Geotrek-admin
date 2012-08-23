-------------------------------------------------------------------------------
-- Automatic link between Troncon and Commune/Zonage/Secteur
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS troncons_couches_sig_d_tgr ON evenements_troncons;

CREATE OR REPLACE FUNCTION lien_auto_troncon_couches_sig_d() RETURNS trigger AS $$
DECLARE
    tab varchar;
BEGIN
    FOREACH tab IN ARRAY ARRAY[['commune', 'secteur', 'zonage']]
    LOOP
        -- Delete related object in association tables
        EXECUTE 'DELETE FROM '|| quote_ident(tab) ||' WHERE evenement = $1' USING OLD.evenement;
        -- TODO: Related evenement will be cleared by a more general trigger
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER troncons_couches_sig_d_tgr
AFTER DELETE ON evenements_troncons
FOR EACH ROW EXECUTE PROCEDURE lien_auto_troncon_couches_sig_d();



-------------------------------------------------------------------------------
-- Evenements utilities
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_troncon_interpolate(troncon integer, point geometry) RETURNS RECORD AS $$
DECLARE 
  line GEOMETRY;
  result RECORD;
BEGIN
    SELECT geom FROM troncons WHERE id=troncon INTO line;
    SELECT * FROM ST_InterpolateAlong(line, point) AS (position FLOAT, distance FLOAT) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-------------------------------------------------------------------------------
-- Compute geometry of Evenements
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_troncons_geometry_tgr ON evenements_troncons;

CREATE OR REPLACE FUNCTION ft_evenements_troncons_geometry() RETURNS trigger AS $$
DECLARE
    eid integer;
    eids integer[];
    egeom geometry;
    lines_only boolean;
    t_count integer;
BEGIN
    IF TG_OP = 'INSERT' THEN
        eids := array_append(eids, NEW.evenement);
    ELSE
        eids := array_append(eids, OLD.evenement);
        IF TG_OP = 'UPDATE' THEN -- /!\ Logical ops are commutative in SQL
            IF NEW.evenement != OLD.evenement THEN
                eids := array_append(eids, NEW.evenement);
            END IF;
        END IF;
    END IF;

    FOREACH eid IN ARRAY eids LOOP
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
            CONTINUE;
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

        -- TODO: DELETE evenements_troncons ON DELETE OR UPDATE supprime ON evenements (disable this trigger)
        -- TODO: UPDATE evenements ON UPDATE decallage ON evenement
        -- TODO: UPDATE evenements ON UPDATE geom ON troncons
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER evenements_troncons_geometry_tgr
AFTER INSERT OR UPDATE OR DELETE ON evenements_troncons
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_geometry();
