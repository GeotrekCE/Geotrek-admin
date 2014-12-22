-------------------------------------------------------------------------------
-- Alter FK to troncon in order to add CASCADE behavior at DB-level
-------------------------------------------------------------------------------

DO LANGUAGE plpgsql $$
DECLARE
    fk_name varchar;
BEGIN
    -- Obtain FK name (which is dynamically generated when table is created)
    SELECT c.conname INTO fk_name
        FROM pg_class t1, pg_class t2, pg_constraint c
        WHERE t1.relname = 'e_r_evenement_troncon' AND c.conrelid = t1.oid
          AND t2.relname = 'l_t_troncon' AND c.confrelid = t2.oid
          AND c.contype = 'f';
    -- Use a dynamic SQL statement with the name found
    IF fk_name IS NOT NULL THEN
        EXECUTE 'ALTER TABLE e_r_evenement_troncon DROP CONSTRAINT ' || quote_ident(fk_name);
    END IF;
END;
$$;

-- Now re-create the FK with cascade option
ALTER TABLE e_r_evenement_troncon ADD FOREIGN KEY (troncon) REFERENCES l_t_troncon(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;


-------------------------------------------------------------------------------
-- Evenements utilities
-------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION geotrek.ft_troncon_interpolate(troncon integer, point geometry) RETURNS RECORD AS $$
DECLARE 
  line GEOMETRY;
  result RECORD;
BEGIN
    SELECT geom FROM l_t_troncon WHERE id=troncon INTO line;
    SELECT * FROM ST_InterpolateAlong(line, point) AS (position FLOAT, distance FLOAT) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


-------------------------------------------------------------------------------
-- Compute geometry of Evenements
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_r_evenement_troncon_geometry_tgr ON e_r_evenement_troncon;

CREATE OR REPLACE FUNCTION geotrek.ft_evenements_troncons_geometry() RETURNS trigger AS $$
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
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER e_r_evenement_troncon_geometry_tgr
AFTER INSERT OR UPDATE OR DELETE ON e_r_evenement_troncon
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_geometry();


-------------------------------------------------------------------------------
-- Emulate junction points
-------------------------------------------------------------------------------

DROP TRIGGER IF EXISTS e_r_evenement_troncon_junction_point_iu_tgr ON e_r_evenement_troncon;

CREATE OR REPLACE FUNCTION geotrek.ft_evenements_troncons_junction_point_iu() RETURNS trigger AS $$
DECLARE
    junction geometry;
    t_count integer;
BEGIN
    -- Deal with previously connected paths in the case of an UDPATE action
    IF TG_OP = 'UPDATE' THEN
        -- There were connected paths only if it was a junction point
        IF OLD.pk_debut = OLD.pk_fin AND OLD.pk_debut IN (0.0, 1.0) THEN
            DELETE FROM e_r_evenement_troncon
            WHERE id != OLD.id AND evenement = OLD.evenement;
        END IF;
    END IF;

    -- Don't proceed for non-junction points
    IF NEW.pk_debut != NEW.pk_fin OR NEW.pk_debut NOT IN (0.0, 1.0) THEN
        RETURN NULL;
    END IF;

    -- Don't proceed for intermediate markers (forced passage) : if this 
    -- is not the only evenement_troncon, then it's an intermediate marker.
    SELECT count(*)
        INTO t_count
        FROM e_r_evenement_troncon et
        WHERE et.evenement = NEW.evenement;
    IF t_count > 1 THEN
        RETURN NULL;
    END IF;

    -- Deal with newly connected paths
    IF NEW.pk_debut = 0.0 THEN
        SELECT ST_StartPoint(geom) INTO junction FROM l_t_troncon WHERE id = NEW.troncon;
    ELSIF NEW.pk_debut = 1.0 THEN
        SELECT ST_EndPoint(geom) INTO junction FROM l_t_troncon WHERE id = NEW.troncon;
    END IF;

    INSERT INTO e_r_evenement_troncon (troncon, evenement, pk_debut, pk_fin)
    SELECT id, NEW.evenement, 0.0, 0.0 -- Troncon departing from this junction
    FROM l_t_troncon t
    WHERE id != NEW.troncon AND ST_StartPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM e_r_evenement_troncon WHERE troncon = t.id AND evenement = NEW.evenement
    )
    UNION
    SELECT id, NEW.evenement, 1.0, 1.0-- Troncon arriving at this junction
    FROM l_t_troncon t
    WHERE id != NEW.troncon AND ST_EndPoint(geom) = junction AND NOT EXISTS (
        -- prevent trigger recursion
        SELECT * FROM e_r_evenement_troncon WHERE troncon = t.id AND evenement = NEW.evenement
    );

    RETURN NULL;
END;
$$ LANGUAGE plpgsql VOLATILE;
-- VOLATILE is the default but I prefer to set it explicitly because it is
-- required for this case (in order to avoid trigger cascading)

CREATE TRIGGER e_r_evenement_troncon_junction_point_iu_tgr
AFTER INSERT OR UPDATE OF pk_debut, pk_fin ON e_r_evenement_troncon
FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_junction_point_iu();
