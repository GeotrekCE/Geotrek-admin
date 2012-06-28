------------------------------------------------------------------------------
-- date_insert field on troncons, evenements
------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_date_insert() RETURNS trigger AS $$
BEGIN
    NEW.date_insert := current_timestamp;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS ti_date ON troncons;
CREATE TRIGGER ti_date
    BEFORE INSERT ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

DROP TRIGGER IF EXISTS ti_date ON evenements;
CREATE TRIGGER ti_date
    BEFORE INSERT ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_insert();

------------------------------------------------------------------------------
-- date_update field on troncons, evenements
------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_date_update() RETURNS trigger AS $$
BEGIN
    NEW.date_update := current_timestamp;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tu_date ON troncons;
CREATE TRIGGER tu_date
    BEFORE INSERT OR UPDATE ON troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

DROP TRIGGER IF EXISTS tu_date ON evenements;
CREATE TRIGGER tu_date
    BEFORE INSERT OR UPDATE ON evenements
    FOR EACH ROW EXECUTE PROCEDURE ft_date_update();

------------------------------------------------------------------------------
-- geom and longueur fields on evenements when evenements_troncons changed
------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ft_evenements_troncons_changed() RETURNS trigger AS $$
DECLARE
    new_geom geometry;
    evts integer[];
BEGIN
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        evts := array_append(evenements, NEW.evenement);
    END IF;
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        evts := array_append(evenements, OLD.evenement);
    END IF;
    FOR i IN 1 .. array_length(evts, 1) LOOP
        -- TODO: use only pk_debut->pk_fin of each geometry
        -- TODO: apply decallage
        SELECT ST_Multi(ST_LineMerge(ST_Collect(t.geom))) INTO new_geom
        FROM troncons t, evenements_troncons et
        WHERE et.troncon = t.id AND et.evenement = evts[i];

        UPDATE evenements SET geom = new_geom, longueur = ST_Length(new_geom)
        WHERE id = evts[i];
    END LOOP;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS t_evenements_troncons ON evenements_troncons;
CREATE TRIGGER t_evenements_troncons
    AFTER INSERT OR UPDATE OR DELETE ON evenements_troncons
    FOR EACH ROW EXECUTE PROCEDURE ft_evenements_troncons_changed();

------------------------------------------------------------------------------
-- geom and longueur fields on evenements when troncons changed
------------------------------------------------------------------------------

-- TODO
