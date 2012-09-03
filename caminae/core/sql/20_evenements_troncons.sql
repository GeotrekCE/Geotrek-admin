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


-------------------------------------------------------------------------------
-- Compute geometry of Evenements
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS evenements_troncons_junction_point_iu_tgr ON evenements_troncons;

CREATE OR REPLACE FUNCTION ft_evenements_troncons_junction_point_iu() RETURNS trigger AS $$
DECLARE
    junction geometry;
BEGIN
    -- Don't proceed for non-junction points
    IF NEW.pk_debut != NEW.pk_fin OR NEW.pk_debut NOT IN (0.0, 1.0) THEN
        RETURN NEW;
    END IF;

    IF NEW.pk_debut = 0.0 THEN
        SELECT ST_StartPoint(geom) INTO junction FROM troncons WHERE id = NEW.troncon;
    ELSIF NEW.pk_debut = 1.0 THEN
        SELECT ST_EndPoint(geom) INTO junction FROM troncons WHERE id = NEW.troncon;
    END IF;

    INSERT INTO evenements_troncons (troncon, evenement, pk_debut, pk_fin)
    SELECT id, NEW.evenement, 0.0, 0.0 -- Troncon departing from this junction
    FROM troncons t
    WHERE id != NEW.troncon AND ST_StartPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM evenements_troncons WHERE troncon = t.id AND evenement = NEW.evenement
    )
    UNION
    SELECT id, NEW.evenement, 1.0, 1.0-- Troncon arriving at this junction
    FROM troncons t
    WHERE id != NEW.troncon AND ST_EndPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM evenements_troncons WHERE troncon = t.id AND evenement = NEW.evenement
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql VOLATILE;
-- VOLATILE is the default but I prefer to set it explicitly because it is
-- required for this case (in order to avoid trigger cascading)

CREATE TRIGGER evenements_troncons_junction_point_iu_tgr
AFTER INSERT OR UPDATE ON evenements_troncons
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_junction_point_iu();
