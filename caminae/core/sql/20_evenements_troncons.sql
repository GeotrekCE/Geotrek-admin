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
        PERFORM update_geometry_of_evenement(eid);

        -- TODO: DELETE evenements_troncons ON DELETE OR UPDATE supprime ON evenements (disable this trigger)
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER evenements_troncons_geometry_tgr
AFTER INSERT OR UPDATE OR DELETE ON evenements_troncons
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_geometry();
